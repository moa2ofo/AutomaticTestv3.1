#!/usr/bin/env python3
"""Generate expanded EtherCAT SSC CiA402 application files from a CANopen EDS.

The generator uses an existing Beckhoff SSC cia402 application .c/.h pair as a
behavioural template and regenerates the axis object model from the EDS:
- structured object typedefs
- CiA402Objects fields
- SDO entry descriptors and names
- default object values
- DefCiA402AxisObjDic
- pointer binding switch in CiA402_Init()

By default CANopen communication-profile objects are not imported, because the
EtherCAT SSC already owns or replaces most objects in 0x1000..0x1FFF. PDO
mapping objects 0x1600..0x17FF and 0x1A00..0x1BFF are included.
"""

from __future__ import annotations

import argparse
import configparser
import dataclasses
import pathlib
import re
import sys
from typing import Iterable


TYPE_MAP = {
    0x0001: ("BOOL", "DEFTYPE_BOOLEAN", 8),
    0x0002: ("INT8", "DEFTYPE_INTEGER8", 8),
    0x0003: ("INT16", "DEFTYPE_INTEGER16", 16),
    0x0004: ("INT32", "DEFTYPE_INTEGER32", 32),
    0x0005: ("UINT8", "DEFTYPE_UNSIGNED8", 8),
    0x0006: ("UINT16", "DEFTYPE_UNSIGNED16", 16),
    0x0007: ("UINT32", "DEFTYPE_UNSIGNED32", 32),
    0x0008: ("REAL32", "DEFTYPE_REAL32", 32),
}

# Existing field names are kept because cia402appl.c directly references them.
FIELD_OVERRIDES = {
    0x1600: "sRxPDOMap0",
    0x1601: "sRxPDOMap1",
    0x1602: "sRxPDOMap2",
    0x1603: "sRxPDOMap3",
    0x1A00: "sTxPDOMap0",
    0x1A01: "sTxPDOMap1",
    0x1A02: "sTxPDOMap2",
    0x1A03: "sTxPDOMap3",
    0x603F: "objErrorCode",
    0x6040: "objControlWord",
    0x6041: "objStatusWord",
    0x605A: "objQuickStopOptionCode",
    0x605B: "objShutdownOptionCode",
    0x605C: "objDisableOperationOptionCode",
    0x605E: "objFaultReactionCode",
    0x6060: "objModesOfOperation",
    0x6061: "objModesOfOperationDisplay",
    0x6064: "objPositionActualValue",
    0x606C: "objVelocityActualValue",
    0x6077: "objTorqueActualValue",
    0x607A: "objTargetPosition",
    0x607D: "objSoftwarePositionLimit",
    0x6083: "objProfileAcceleration",
    0x6085: "objQuickStopDeclaration",
    0x60C2: "objInterpolationTimePeriod",
    0x60FF: "objTargetVelocity",
    0x6502: "objSupportedDriveModes",
}

# These structured types already exist in the supplied Beckhoff header.
EXISTING_STRUCT_TYPES = {
    0x1600: "TOBJ1600",
    0x1601: "TOBJ1601",
    0x1602: "TOBJ1602",
    0x1A00: "TOBJ1A00",
    0x1A01: "TOBJ1A01",
    0x1A02: "TOBJ1A02",
    0x607D: "TOBJ607D",
    0x60C2: "TOBJ60C2",
}

# 0x605C is used by the Beckhoff state machine but is absent in the supplied EDS.
LEGACY_OBJECTS = {
    0x605C: {
        "name": "Disable Operation Option Code",
        "object_type": 0x7,
        "data_type": 0x0003,
        "access": "rw",
        "default": "1",
        "pdo_mapping": False,
    }
}

# Preserve the sample PDO layout. Other PDO mapping objects are initialized empty.
DEFAULT_OVERRIDES = {
    0x1600: "{3, {0x60400010, 0x607A0020, 0x60600008, 0, 0, 0, 0, 0}}",
    0x1601: "{0, {0, 0, 0, 0, 0, 0, 0, 0}}",
    0x1602: "{0, {0, 0, 0, 0, 0, 0, 0, 0}}",
    0x1A00: "{3, {0x60410010, 0x60640020, 0x60610008, 0, 0, 0, 0, 0}}",
    0x1A01: "{0, {0, 0, 0, 0, 0, 0, 0, 0}}",
    0x1A02: "{0, {0, 0, 0, 0, 0, 0, 0, 0}}",
    0x605A: "2",              # sample quick-stop behaviour
    0x605C: "SLOW_DOWN_RAMP", # required by existing state machine
    0x605E: "QUICKSTOP_RAMP", # sample fault reaction
    0x607D: "{2, 0x88CA6C00, 0x77359400}",
    0x60C2: "{2, 1, -3}",
}


@dataclasses.dataclass
class Entry:
    subindex: int
    name: str
    data_type: int
    access: str
    default: str
    pdo_mapping: bool


@dataclasses.dataclass
class Obj:
    index: int
    name: str
    object_type: int
    entries: list[Entry]
    source: str = "EDS"
    field_name: str = ""

    @property
    def is_var(self) -> bool:
        return self.object_type == 0x7

    @property
    def max_subindex(self) -> int:
        return max((e.subindex for e in self.entries), default=0)

    @property
    def type_name(self) -> str:
        if self.is_var:
            return c_type(self.entries[0].data_type)
        return EXISTING_STRUCT_TYPES.get(self.index, f"TOBJ{self.index:04X}")


class GenerationError(RuntimeError):
    pass


def parse_int(value: str | None, default: int = 0) -> int:
    if value is None or not value.strip():
        return default
    return int(value.strip(), 0)


def c_type(data_type: int) -> str:
    try:
        return TYPE_MAP[data_type][0]
    except KeyError as exc:
        raise GenerationError(f"Unsupported EDS DataType 0x{data_type:04X}") from exc


def def_type(data_type: int) -> str:
    try:
        return TYPE_MAP[data_type][1]
    except KeyError as exc:
        raise GenerationError(f"Unsupported EDS DataType 0x{data_type:04X}") from exc


def bit_length(data_type: int) -> int:
    try:
        return TYPE_MAP[data_type][2]
    except KeyError as exc:
        raise GenerationError(f"Unsupported EDS DataType 0x{data_type:04X}") from exc


def section_key(index: int, subindex: int | None = None) -> str:
    if subindex is None:
        return f"{index:04X}"
    return f"{index:04X}sub{subindex:X}"


def load_eds(path: pathlib.Path) -> tuple[dict[int, Obj], list[str]]:
    cfg = configparser.ConfigParser(interpolation=None, strict=False)
    cfg.optionxform = str
    with path.open("r", encoding="utf-8-sig", errors="replace") as fh:
        cfg.read_file(fh)

    sections = {s.upper(): s for s in cfg.sections()}
    base_re = re.compile(r"^([0-9A-F]{4})$")
    warnings: list[str] = []
    objects: dict[int, Obj] = {}

    for upper_name, real_name in sections.items():
        match = base_re.fullmatch(upper_name)
        if not match:
            continue
        index = int(match.group(1), 16)
        base = cfg[real_name]
        object_type = parse_int(base.get("ObjectType"), 0x7)
        name = base.get("ParameterName", f"Object 0x{index:04X}").strip()
        entries: list[Entry] = []

        if object_type == 0x7:
            try:
                data_type = parse_int(base.get("DataType"))
                if data_type not in TYPE_MAP:
                    warnings.append(
                        f"0x{index:04X} skipped: unsupported DataType 0x{data_type:04X}"
                    )
                    continue
                entries.append(
                    Entry(
                        subindex=0,
                        name=name,
                        data_type=data_type,
                        access=base.get("AccessType", "ro").lower(),
                        default=base.get("DefaultValue", "0").strip(),
                        pdo_mapping=base.get("PDOMapping", "0").strip() == "1",
                    )
                )
            except ValueError:
                warnings.append(f"0x{index:04X} skipped: invalid DataType")
                continue
        elif object_type in (0x8, 0x9):
            sub_sections: list[tuple[int, configparser.SectionProxy]] = []
            prefix = f"{index:04X}SUB"
            for sub_upper, sub_real in sections.items():
                if not sub_upper.startswith(prefix):
                    continue
                suffix = sub_upper[len(prefix):]
                if not suffix or not re.fullmatch(r"[0-9A-F]+", suffix):
                    continue
                sub_sections.append((int(suffix, 16), cfg[sub_real]))
            sub_sections.sort(key=lambda item: item[0])
            if not sub_sections:
                warnings.append(f"0x{index:04X} skipped: no subindex sections")
                continue
            supported = True
            for subindex, sec in sub_sections:
                data_type = parse_int(sec.get("DataType"))
                if data_type not in TYPE_MAP:
                    warnings.append(
                        f"0x{index:04X}:{subindex:02X} skipped: unsupported DataType 0x{data_type:04X}"
                    )
                    supported = False
                    break
                entries.append(
                    Entry(
                        subindex=subindex,
                        name=sec.get("ParameterName", f"SubIndex {subindex}").strip(),
                        data_type=data_type,
                        access=sec.get("AccessType", "ro").lower(),
                        default=sec.get("DefaultValue", "0").strip(),
                        pdo_mapping=sec.get("PDOMapping", "0").strip() == "1",
                    )
                )
            if not supported:
                continue
            actual = [e.subindex for e in entries]
            expected = list(range(0, max(actual) + 1))
            if actual != expected:
                warnings.append(
                    f"0x{index:04X} skipped: non-contiguous subindices {actual}"
                )
                continue
        else:
            warnings.append(
                f"0x{index:04X} skipped: unsupported ObjectType 0x{object_type:X}"
            )
            continue

        objects[index] = Obj(index=index, name=name, object_type=object_type, entries=entries)

    for index, meta in LEGACY_OBJECTS.items():
        if index in objects:
            continue
        objects[index] = Obj(
            index=index,
            name=str(meta["name"]),
            object_type=int(meta["object_type"]),
            source="template compatibility",
            entries=[
                Entry(
                    subindex=0,
                    name=str(meta["name"]),
                    data_type=int(meta["data_type"]),
                    access=str(meta["access"]),
                    default=str(meta["default"]),
                    pdo_mapping=bool(meta["pdo_mapping"]),
                )
            ],
        )

    return objects, warnings


def select_objects(objects: dict[int, Obj], include_communication: bool) -> tuple[list[Obj], list[int]]:
    selected: list[Obj] = []
    skipped_communication: list[int] = []
    for index, obj in sorted(objects.items()):
        keep = (
            0x1600 <= index <= 0x17FF
            or 0x1A00 <= index <= 0x1BFF
            or 0x2000 <= index <= 0x5FFF
            or 0x6000 <= index <= 0x67FF
        )
        if include_communication and 0x1000 <= index <= 0x1FFF:
            keep = True
        elif 0x1000 <= index <= 0x1FFF and not keep:
            skipped_communication.append(index)
        if keep:
            selected.append(obj)
    return selected, skipped_communication


def sanitize_identifier(text: str, prefix: str = "") -> str:
    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        result = "Value"
    else:
        result = "".join(w[:1].upper() + w[1:] for w in words)
    if result[0].isdigit():
        result = "N" + result
    return prefix + result


def assign_field_names(objects: list[Obj]) -> None:
    used: set[str] = set()
    for obj in objects:
        candidate = FIELD_OVERRIDES.get(obj.index)
        if candidate is None:
            if 0x1600 <= obj.index <= 0x17FF:
                candidate = f"sRxPDOMap{obj.index - 0x1600}"
            elif 0x1A00 <= obj.index <= 0x1BFF:
                candidate = f"sTxPDOMap{obj.index - 0x1A00}"
            else:
                candidate = sanitize_identifier(obj.name, "obj")
        if candidate in used:
            candidate = f"{candidate}_{obj.index:04X}"
        used.add(candidate)
        obj.field_name = candidate


def homogeneous_payload(obj: Obj) -> bool:
    payload = [e for e in obj.entries if e.subindex != 0]
    return bool(payload) and len({e.data_type for e in payload}) == 1


def field_for_entry(entry: Entry, used: set[str]) -> str:
    if entry.subindex == 0:
        return "u16SubIndex0"
    candidate = sanitize_identifier(entry.name)
    candidate = candidate[:1].lower() + candidate[1:]
    if not candidate or candidate in used:
        candidate = f"subIndex{entry.subindex:X}"
    if candidate[0].isdigit():
        candidate = "subIndex" + candidate
    used.add(candidate)
    return candidate


def render_struct_type(obj: Obj) -> str:
    if obj.is_var or obj.index in EXISTING_STRUCT_TYPES:
        return ""
    lines = [
        f"/** \\brief Object 0x{obj.index:04X} ({obj.name}) data structure. */",
        "typedef struct OBJ_STRUCT_PACKED_START",
        "{",
        "    UINT16 u16SubIndex0; /**< \\brief SubIndex 0, stored as UINT16 by SSC. */",
    ]
    payload = [e for e in obj.entries if e.subindex != 0]
    if homogeneous_payload(obj):
        lines.append(
            f"    {c_type(payload[0].data_type)} aEntries[{len(payload)}]; /**< \\brief SubIndex 1..{len(payload)}. */"
        )
    else:
        used = {"u16SubIndex0"}
        for entry in payload:
            name = field_for_entry(entry, used)
            lines.append(
                f"    {c_type(entry.data_type)} {name}; /**< \\brief 0x{obj.index:04X}:{entry.subindex:02X} {entry.name}. */"
            )
    lines += ["} OBJ_STRUCT_PACKED_END", f"TOBJ{obj.index:04X};", ""]
    return "\n".join(lines)


def render_generated_types(objects: list[Obj]) -> str:
    body = "\n".join(filter(None, (render_struct_type(o) for o in objects)))
    return (
        "/* BEGIN GENERATED EDS OBJECT TYPES */\n"
        "/* Generated by generate_cia402.py. Do not edit this block manually. */\n"
        + body
        + "/* END GENERATED EDS OBJECT TYPES */\n\n"
    )


def render_objects_struct(objects: list[Obj]) -> str:
    lines = [
        "/** \\brief Data structure containing all selected EDS axis/manufacturer objects. */",
        "typedef struct OBJ_STRUCT_PACKED_START",
        "{",
    ]
    for obj in objects:
        lines.append(
            f"    {obj.type_name} {obj.field_name}; /**< \\brief 0x{obj.index:04X} {obj.name}. */"
        )
    lines += ["} OBJ_STRUCT_PACKED_END", "CiA402Objects;"]
    return "\n".join(lines)


def access_expression(entry: Entry, rw_pdo_direction: str) -> str:
    access = entry.access.lower()
    if access in {"ro", "const"}:
        flags = ["ACCESS_READ"]
    elif access == "wo":
        flags = ["ACCESS_WRITE"]
    else:
        flags = ["ACCESS_READWRITE"]

    if entry.pdo_mapping:
        if access in {"ro", "const"}:
            flags.append("OBJACCESS_TXPDOMAPPING")
        elif access == "wo":
            flags.append("OBJACCESS_RXPDOMAPPING")
        else:
            flags.append("OBJACCESS_RXPDOMAPPING")
            if rw_pdo_direction == "both":
                flags.append("OBJACCESS_TXPDOMAPPING")
    return "(" + " | ".join(flags) + ")" if len(flags) > 1 else flags[0]


def c_string(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def render_descriptors(objects: list[Obj], rw_pdo_direction: str, block_name: str = "ENTRY") -> str:
    lines = [
        f"/* BEGIN GENERATED EDS {block_name} DESCRIPTORS */",
        "/* Generated by generate_cia402.py. Do not edit this block manually. */",
    ]
    for obj in objects:
        lines.append(f"\n/** \\brief Object 0x{obj.index:04X} ({obj.name}) descriptors. */")
        if obj.is_var:
            entry = obj.entries[0]
            lines.append(
                f"OBJCONST TSDOINFOENTRYDESC OBJMEM sEntryDesc0x{obj.index:04X} = "
                f"{{{def_type(entry.data_type)}, 0x{bit_length(entry.data_type):02X}, {access_expression(entry, rw_pdo_direction)}}};"
            )
            lines.append(
                f'OBJCONST UCHAR OBJMEM aName0x{obj.index:04X}[] = "{c_string(obj.name)}";'
            )
        else:
            lines.append(
                f"OBJCONST TSDOINFOENTRYDESC OBJMEM asEntryDesc0x{obj.index:04X}[] ="
            )
            lines.append("{")
            for entry in obj.entries:
                lines.append(
                    f"    {{{def_type(entry.data_type)}, 0x{bit_length(entry.data_type):02X}, "
                    f"{access_expression(entry, rw_pdo_direction)}}}, /* SubIndex 0x{entry.subindex:02X} */"
                )
            lines.append("};")
            names = [obj.name] + [e.name for e in obj.entries if e.subindex != 0]
            encoded = "\\000".join(c_string(n) for n in names) + "\\000\\377"
            lines.append(
                f'OBJCONST UCHAR OBJMEM aName0x{obj.index:04X}[] = "{encoded}";'
            )
    lines += ["", f"/* END GENERATED EDS {block_name} DESCRIPTORS */"]
    return "\n".join(lines)


def normalize_number(raw: str, data_type: int) -> str:
    value = raw.strip() if raw is not None else "0"
    if not value:
        value = "0"
    if "$NODEID" in value.upper():
        value = re.sub(r"\$NODEID", "0", value, flags=re.IGNORECASE)
    if data_type == 0x0008:
        try:
            number = float(value)
            if number == int(number):
                return f"{int(number)}.0F"
            return f"{number:.9g}F"
        except ValueError:
            return value
    try:
        number = int(value, 0)
    except ValueError:
        return value
    if value.lower().startswith("0x"):
        return f"0x{number:X}"
    return str(number)


def object_default(obj: Obj) -> str:
    if obj.index in DEFAULT_OVERRIDES:
        return DEFAULT_OVERRIDES[obj.index]
    if obj.is_var:
        return normalize_number(obj.entries[0].default, obj.entries[0].data_type)

    payload = [e for e in obj.entries if e.subindex != 0]
    sub0 = next((e for e in obj.entries if e.subindex == 0), None)
    sub0_value = normalize_number(sub0.default if sub0 else str(len(payload)), 0x0005)

    # Empty PDO mappings must have SI0 = 0 even if the EDS exports SI0 = 8.
    if 0x1600 <= obj.index <= 0x17FF or 0x1A00 <= obj.index <= 0x1BFF:
        mapped = [normalize_number(e.default, e.data_type) for e in payload]
        nonzero = sum(v not in {"0", "0x0", "0x00000000"} for v in mapped)
        sub0_value = str(nonzero)

    values = [normalize_number(e.default, e.data_type) for e in payload]
    if homogeneous_payload(obj):
        return "{" + sub0_value + ", {" + ", ".join(values) + "}}"
    return "{" + ", ".join([sub0_value] + values) + "}"


def render_defaults(objects: list[Obj]) -> str:
    lines = [
        "/** \\brief Axis object default values generated from the EDS. */",
        "PROTO CiA402Objects DefCiA402ObjectValues",
        "#ifdef _CiA402_",
        "=",
        "{",
    ]
    for pos, obj in enumerate(objects):
        comma = "," if pos + 1 < len(objects) else ""
        lines.append(
            f"    {object_default(obj)}{comma} /* 0x{obj.index:04X} {obj.name} */"
        )
    lines += ["}", "#endif", ";"]
    return "\n".join(lines)


def dictionary_type(obj: Obj) -> str:
    if obj.is_var:
        return def_type(obj.entries[0].data_type)
    if 0x1600 <= obj.index <= 0x17FF or 0x1A00 <= obj.index <= 0x1BFF:
        return "DEFTYPE_PDOMAPPING"
    if obj.object_type == 0x8:
        payload = [e for e in obj.entries if e.subindex != 0]
        return def_type(payload[0].data_type)
    return "DEFTYPE_RECORD"


def dictionary_code(obj: Obj) -> str:
    if obj.is_var:
        return "OBJCODE_VAR"
    if 0x1600 <= obj.index <= 0x17FF or 0x1A00 <= obj.index <= 0x1BFF:
        return "OBJCODE_REC"
    return "OBJCODE_ARR" if obj.object_type == 0x8 else "OBJCODE_REC"


def descriptor_pointer(obj: Obj) -> str:
    return f"&sEntryDesc0x{obj.index:04X}" if obj.is_var else f"asEntryDesc0x{obj.index:04X}"


def render_dictionary(objects: list[Obj]) -> str:
    lines = [
        "/** \\brief Object dictionary related to one CiA402 axis. */",
        "PROTO TOBJECT OBJMEM DefCiA402AxisObjDic[]",
        "#ifdef _CiA402_",
        "=",
        "{",
    ]
    for obj in objects:
        lines.append(
            f"    {{NULL, NULL, 0x{obj.index:04X}, "
            f"{{{dictionary_type(obj)}, {obj.max_subindex} | ({dictionary_code(obj)} << 8)}}, "
            f"{descriptor_pointer(obj)}, aName0x{obj.index:04X}, NULL, NULL, NULL, 0x0000}},"
        )
    lines += [
        "    {NULL, NULL, 0xFFFF, {0, 0}, NULL, NULL, NULL, NULL, NULL, 0x0000}",
        "}",
        "#endif",
        ";",
    ]
    return "\n".join(lines)


def render_switch_cases(objects: list[Obj]) -> str:
    lines: list[str] = []
    for obj in objects:
        lines += [
            f"            case 0x{obj.index:04X}:",
            f"                pDiCEntry->pVarPtr = &LocalAxes[AxisCnt].Objects.{obj.field_name};",
            "                break;",
        ]
    return "\n".join(lines) + "\n"


def replace_once(text: str, pattern: str, replacement: str, description: str, flags: int = re.S) -> str:
    result, count = re.subn(pattern, lambda _m: replacement, text, count=1, flags=flags)
    if count != 1:
        raise GenerationError(f"Unable to replace {description}; expected one match, got {count}")
    return result


def patch_header(template: str, objects: list[Obj], rw_pdo_direction: str, output_name: str) -> str:
    text = template
    text = re.sub(
        r"/\* BEGIN GENERATED EDS OBJECT TYPES \*/.*?/\* END GENERATED EDS OBJECT TYPES \*/\s*",
        "",
        text,
        flags=re.S,
    )

    struct_anchor = "/** \\brief Data structure to handle the axis specific object data*/"
    pos = text.find(struct_anchor)
    if pos < 0:
        raise GenerationError("Cannot find CiA402Objects structure anchor in header template")
    text = text[:pos] + render_generated_types(objects) + text[pos:]

    text = replace_once(
        text,
        r"/\*\* \\brief Data structure to handle the axis specific object data\*/\s*"
        r"typedef struct OBJ_STRUCT_PACKED_START\s*\{.*?\}\s*OBJ_STRUCT_PACKED_END\s*CiA402Objects;",
        render_objects_struct(objects),
        "CiA402Objects structure",
    )

    pdo_objects = [o for o in objects if (0x1600 <= o.index <= 0x17FF) or (0x1A00 <= o.index <= 0x1BFF)]
    axis_objects = [o for o in objects if o not in pdo_objects]

    pdo_start = text.find("/**\n* \\addtogroup PdoMappingObjects PDO Mapping Objects")
    if pdo_start < 0:
        pdo_start = text.find("/**\n * \\addtogroup PdoMappingObjects PDO Mapping Objects")
    axis_group = text.find("/**\n * \\addtogroup CiA402Objects CiA402 Axis Objects", pdo_start)
    if pdo_start < 0 or axis_group < 0:
        raise GenerationError("Cannot find PDO descriptor group in header template")
    pdo_group = (
        "/**\n * \\addtogroup PdoMappingObjects PDO Mapping Objects\n * @{\n */\n"
        + render_descriptors(pdo_objects, rw_pdo_direction, "PDO")
        + "\n/** @}*/\n\n"
    )
    text = text[:pdo_start] + pdo_group + text[axis_group:]

    desc_start = text.find(" /*ECATCHANGE_START(V5.13) CIA402 1*/")
    if desc_start < 0:
        desc_start = text.find("/*ECATCHANGE_START(V5.13) CIA402 1*/")
    if desc_start < 0:
        raise GenerationError("Cannot find descriptor block start")
    desc_end = text.find("/** @}*/", desc_start)
    if desc_end < 0:
        raise GenerationError("Cannot find descriptor block end")
    desc_end += len("/** @}*/")
    text = text[:desc_start] + render_descriptors(axis_objects, rw_pdo_direction, "AXIS") + "\n/** @}*/" + text[desc_end:]

    text = replace_once(
        text,
        r"/\*\*\s*\n \* \\brief Axis objects default values.*?PROTO CiA402Objects DefCiA402ObjectValues.*?#endif\s*;",
        render_defaults(objects),
        "DefCiA402ObjectValues",
    )

    text = replace_once(
        text,
        r"/\*\*\s*\n \*\\brief Object dictionary related to on CiA402 Axis\s*\n \*/\s*"
        r"PROTO TOBJECT\s+OBJMEM DefCiA402AxisObjDic\[\].*?#endif\s*;",
        render_dictionary(objects),
        "DefCiA402AxisObjDic",
    )

    text = text.replace("\\file cia402appl.h", f"\\file {output_name}")
    return text


def patch_source(template: str, objects: list[Obj], header_name: str, output_name: str) -> str:
    text = template.replace('"cia402appl.h"', f'"{header_name}"')
    text = text.replace("\\file cia402appl.c", f"\\file {output_name}")
    switch_pattern = (
        r"(switch\s*\(pDiCEntry->Index\)\s*\{\s*)"
        r".*?"
        r"(\s*default\s*:)"
    )
    match = re.search(switch_pattern, text, flags=re.S)
    if not match:
        raise GenerationError("Cannot find object pointer switch in source template")
    replacement = match.group(1) + render_switch_cases(objects) + match.group(2)
    text = text[:match.start()] + replacement + text[match.end():]
    return text


def validate_generated(header: str, source: str, objects: list[Obj]) -> list[str]:
    issues: list[str] = []
    for obj in objects:
        idx = f"0x{obj.index:04X}"
        if idx not in header:
            issues.append(f"Header does not contain {idx}")
        if f"case {idx}:" not in source:
            issues.append(f"Source does not bind {idx}")
        if f"Objects.{obj.field_name}" not in source:
            issues.append(f"Source does not reference field {obj.field_name}")
    if header.count("PROTO CiA402Objects DefCiA402ObjectValues") != 1:
        issues.append("Unexpected number of DefCiA402ObjectValues definitions")
    if header.count("PROTO TOBJECT OBJMEM DefCiA402AxisObjDic[]") != 1:
        issues.append("Unexpected number of DefCiA402AxisObjDic definitions")
    return issues


def build_report(
    eds_path: pathlib.Path,
    h_template: pathlib.Path,
    c_template: pathlib.Path,
    selected: list[Obj],
    skipped_communication: list[int],
    warnings: list[str],
    include_communication: bool,
    validation_issues: list[str],
) -> str:
    lines = [
        "CiA402 generation report",
        "========================",
        f"EDS: {eds_path}",
        f"Header template: {h_template}",
        f"Source template: {c_template}",
        f"Selected objects: {len(selected)}",
        f"Include CANopen communication objects: {include_communication}",
        "",
        "Selected indexes:",
    ]
    for obj in selected:
        lines.append(
            f"  0x{obj.index:04X}  {obj.name}  field={obj.field_name}  source={obj.source}"
        )
    if skipped_communication:
        lines += [
            "",
            "CANopen communication objects intentionally not imported by default:",
            "  " + ", ".join(f"0x{i:04X}" for i in skipped_communication),
            "Use --include-communication only after checking conflicts with the SSC object dictionary.",
        ]
    if warnings:
        lines += ["", "Parser warnings:"] + [f"  - {w}" for w in warnings]
    if validation_issues:
        lines += ["", "Validation issues:"] + [f"  - {w}" for w in validation_issues]
    else:
        lines += ["", "Static generator validation: OK"]
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eds", required=True, type=pathlib.Path)
    parser.add_argument("--template-c", required=True, type=pathlib.Path)
    parser.add_argument("--template-h", required=True, type=pathlib.Path)
    parser.add_argument("--out-c", default=pathlib.Path("cia402.c"), type=pathlib.Path)
    parser.add_argument("--out-h", default=pathlib.Path("cia402.h"), type=pathlib.Path)
    parser.add_argument(
        "--report", default=pathlib.Path("cia402_generation_report.txt"), type=pathlib.Path
    )
    parser.add_argument(
        "--include-communication",
        action="store_true",
        help="also import EDS objects in 0x1000..0x1FFF; may conflict with EtherCAT SSC",
    )
    parser.add_argument(
        "--rw-pdo-direction",
        choices=("rx", "both"),
        default="rx",
        help="PDO mapping flags for rw objects (default follows Beckhoff sample: RxPDO)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        all_objects, warnings = load_eds(args.eds)
        selected, skipped_communication = select_objects(
            all_objects, include_communication=args.include_communication
        )
        assign_field_names(selected)
        if not selected:
            raise GenerationError("No objects selected from EDS")

        h_template = args.template_h.read_text(encoding="utf-8", errors="replace")
        c_template = args.template_c.read_text(encoding="utf-8", errors="replace")
        generated_h = patch_header(
            h_template, selected, args.rw_pdo_direction, args.out_h.name
        )
        generated_c = patch_source(c_template, selected, args.out_h.name, args.out_c.name)
        validation_issues = validate_generated(generated_h, generated_c, selected)

        args.out_h.parent.mkdir(parents=True, exist_ok=True)
        args.out_c.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with args.out_h.open("w", encoding="utf-8", newline="\n") as output_file:
            output_file.write(generated_h)

        with args.out_c.open("w", encoding="utf-8", newline="\n") as output_file:
            output_file.write(generated_c)

        report_text = build_report(
            args.eds,
            args.template_h,
            args.template_c,
            selected,
            skipped_communication,
            warnings,
            args.include_communication,
            validation_issues,
        )
        with args.report.open("w", encoding="utf-8", newline="\n") as output_file:
            output_file.write(report_text)

        print(f"Generated {args.out_h} and {args.out_c} ({len(selected)} objects)")
        print(f"Report: {args.report}")
        if validation_issues:
            for issue in validation_issues:
                print(f"validation: {issue}", file=sys.stderr)
            return 2
        return 0
    except (OSError, ValueError, GenerationError, configparser.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
