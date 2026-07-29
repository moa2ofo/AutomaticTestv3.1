import os
import canopen
from tabulate import tabulate

# Percorso dell'EDS
EDS_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "ELAC.eds"          # <-- cambia il nome se diverso
)

od = canopen.import_od(EDS_FILE)


def read_object_dictionary(elac):

    rows = []

    for index in sorted(od.indices):

        obj = od[index]

        # -----------------------------
        # VAR
        # -----------------------------
        if isinstance(obj, canopen.objectdictionary.Variable):

            try:
                value = elac.sdo[index].raw
            except Exception as e:
                value = f"ERROR"

            rows.append([
                f"0x{index:04X}",
                obj.name,
                "-",
                obj.data_type,
                value
            ])

        # -----------------------------
        # RECORD / ARRAY
        # -----------------------------
        else:

            first = True

            for subindex in sorted(obj):

                sub = obj[subindex]

                try:
                    value = elac.sdo[index][subindex].raw
                except Exception:
                    value = "ERROR"

                rows.append([
                    f"0x{index:04X}" if first else "",
                    obj.name if first else "",
                    subindex,
                    sub.data_type,
                    value
                ])

                first = False

    print(tabulate(
        rows,
        headers=[
            "Index",
            "Object",
            "Sub",
            "Type",
            "Value"
        ],
        tablefmt="fancy_grid"
    ))

    return True