"""
Interfaccia grafica EtherCAT con riconnessione automatica per:
- leggere l'angolo lento (0x6063) e l'angolo veloce (0x6064);
- impostare la velocità target (0x60FF) in rad/s.

ASSUNZIONI DA VERIFICARE CON IL FIRMWARE:
1. 0x6063 e 0x6064 contengono un valore angolare espresso in gradi interi.
   Il valore viene normalizzato nell'intervallo [0, 360) usando il modulo 360.
2. La velocità fisica [-2, +2] rad/s è mappata sull'intero intervallo INT32.
   Se il firmware usa un fattore di scala diverso, modificare rad_s_to_int32().
3. Gli oggetti SDO sono accessibili dal nodo EtherCAT selezionato.

Esecuzione:
    python Read_OD.py
"""

import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from lib.ecat_common_func import RpPysoem


READ_INTERVAL_MS = 250
RECONNECT_INTERVAL_S = 2.0
ANGLE_SLOW_INDEX = 0x6064
ANGLE_FAST_INDEX = 0x6063
TARGET_VELOCITY_INDEX = 0x60FF
DC_LINK_VOLTAGE_INDEX = 0x6079
CURRENT_ACTUAL_INDEX = 0x6078
ERROR_FIELD_INDEX = 0x2028
ERROR_FIELD_SUBINDEX = 1

MAX_DC_LINK_VOLTAGE_V = 60.0
MAX_DC_CURRENT_A = 20.0
UINT32_MAX = (2**32) - 1
INT16_MIN = -(2**15)
INT16_MAX = (2**15) - 1

INT32_MIN = -(2**31)
INT32_MAX = (2**31) - 1
VELOCITY_MIN_RAD_S = -2.0
VELOCITY_MAX_RAD_S = 2.0

VELOCITY_OPTIONS = tuple(f"{step / 2:.1f}" for step in range(-4, 5))


def read_sdo_int32(elac, index):
    """Legge un oggetto SDO e restituisce un intero con segno."""
    value = elac.sdo[index].raw

    if isinstance(value, (bytes, bytearray)):
        if len(value) != 4:
            raise ValueError(
                f"0x{index:04X}: attesi 4 byte INT32, ricevuti {len(value)}"
            )
        return int.from_bytes(value, byteorder="little", signed=True)

    return int(value)


def read_sdo_integer(elac, index, subindex=0, byte_length=4, signed=True):
    """Legge un oggetto SDO integer, gestendo byte grezzi o valori già decodificati."""
    if subindex == 0:
        value = elac.sdo[index].raw
    else:
        value = elac.sdo[index][subindex].raw

    if isinstance(value, (bytes, bytearray)):
        if len(value) != byte_length:
            raise ValueError(
                f"0x{index:04X}:{subindex:02X}: attesi {byte_length} byte, "
                f"ricevuti {len(value)}"
            )
        return int.from_bytes(value, byteorder="little", signed=signed)

    return int(value)


def voltage_from_raw(raw_value):
    return ((raw_value * MAX_DC_LINK_VOLTAGE_V) / UINT32_MAX)


def current_from_raw_int16(raw_value):
    return ((raw_value * MAX_DC_CURRENT_A) / INT16_MAX)


ERROR_BITS = (
    (7, "Overcurrent phase U"),
    (6, "Overcurrent phase V"),
    (5, "Overcurrent phase W"),
    (4, "Overcurrent DC"),
    (3, "Overtemperature ambient"),
    (2, "Overtemperature bridge"),
    (1, "Undervoltage DC link"),
    (0, "Overvoltage DC link"),
)


def decode_error_field(raw_value):
    """Restituisce i nomi degli errori attivi nel bitfield 0x2028:01."""
    return [name for bit, name in ERROR_BITS if (int(raw_value) & (1 << bit)) != 0]


def normalize_angle_deg(raw_value):
    """Normalizza un valore angolare espresso in gradi nell'intervallo [0, 360)."""
    return (raw_value*360/2147483647)


def rad_s_to_int32(velocity_rad_s):
    """
    Scala [-2, +2] rad/s sull'intero intervallo INT32.
    Verificare che questa convenzione coincida con quella del firmware.
    """
    velocity = float(velocity_rad_s)

    if not VELOCITY_MIN_RAD_S <= velocity <= VELOCITY_MAX_RAD_S:
        raise ValueError("La velocità deve essere compresa tra -2 e +2 rad/s.")

    if velocity <= VELOCITY_MIN_RAD_S:
        return INT32_MIN
    if velocity >= VELOCITY_MAX_RAD_S:
        return INT32_MAX

    scaled = round((velocity / VELOCITY_MAX_RAD_S) * INT32_MAX)
    return scaled


def write_target_velocity(elac, velocity_rad_s):
    """Scrive 0x60FF come INT32 little-endian con segno."""
    raw_value = rad_s_to_int32(velocity_rad_s)
    payload = raw_value.to_bytes(4, byteorder="little", signed=True)
    elac.sdo.download(TARGET_VELOCITY_INDEX, 0, payload)
    return raw_value


class EtherCATGui:
    def __init__(self, root, rpsoem, elac, connected=True):
        self.root = root
        self.rpsoem = rpsoem
        self.elac = elac
        self.connected = connected
        self.reconnect_in_progress = False
        self.last_reconnect_attempt = 0.0
        self.root.title("EtherCAT - Angoli e velocità")
        self.root.geometry("760x650")
        self.root.minsize(680, 580)

        self.slow_angle_var = tk.StringVar(value="--")
        self.fast_angle_var = tk.StringVar(value="--")
        self.dc_link_voltage_var = tk.StringVar(value="--")
        self.current_actual_var = tk.StringVar(value="--")
        self.error_field_raw_var = tk.StringVar(value="--")
        self.error_field_active_var = tk.StringVar(value="Nessun errore letto")
        self.velocity_var = tk.StringVar(value="0.0")
        self.raw_velocity_var = tk.StringVar(value="Non ancora scritto")
        initial_status = (
            "Connessione EtherCAT attiva"
            if connected
            else "Slave non disponibile: tentativo di riconnessione in corso"
        )
        self.status_var = tk.StringVar(value=initial_status)
        self.last_update_var = tk.StringVar(value="Ultimo aggiornamento: --")

        self._build_ui()
        self._refresh_values()

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main, text="Monitoraggio angoli", font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 8))

        angle_frame = ttk.LabelFrame(main, text="Valori letti dagli SDO", padding=12)
        angle_frame.pack(fill="x", pady=(0, 14))
        angle_frame.columnconfigure(1, weight=1)

        ttk.Label(angle_frame, text="Angolo lento (0x6064):").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=5
        )
        ttk.Label(
            angle_frame, textvariable=self.slow_angle_var, font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=1, sticky="w", pady=5)

        ttk.Label(angle_frame, text="Angolo veloce (0x6063):").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=5
        )
        ttk.Label(
            angle_frame, textvariable=self.fast_angle_var, font=("Segoe UI", 12, "bold")
        ).grid(row=1, column=1, sticky="w", pady=5)

        ttk.Label(angle_frame, textvariable=self.last_update_var).grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )

        measurement_frame = ttk.LabelFrame(
            main, text="Misure ed errori dall'Object Dictionary", padding=12
        )
        measurement_frame.pack(fill="x", pady=(0, 14))
        measurement_frame.columnconfigure(1, weight=1)

        ttk.Label(measurement_frame, text="Tensione DC link (0x6079):").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=4
        )
        ttk.Label(
            measurement_frame, textvariable=self.dc_link_voltage_var,
            font=("Segoe UI", 10, "bold")
        ).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(measurement_frame, text="Corrente attuale (0x6078):").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=4
        )
        ttk.Label(
            measurement_frame, textvariable=self.current_actual_var,
            font=("Segoe UI", 10, "bold")
        ).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(measurement_frame, text="Error field (0x2028:01):").grid(
            row=2, column=0, sticky="nw", padx=(0, 12), pady=4
        )
        ttk.Label(
            measurement_frame, textvariable=self.error_field_raw_var
        ).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(measurement_frame, text="Errori attivi:").grid(
            row=3, column=0, sticky="nw", padx=(0, 12), pady=4
        )
        ttk.Label(
            measurement_frame, textvariable=self.error_field_active_var,
            wraplength=500
        ).grid(row=3, column=1, sticky="w", pady=4)

        velocity_frame = ttk.LabelFrame(
            main, text="Comando velocità target (0x60FF)", padding=12
        )
        velocity_frame.pack(fill="x", pady=(0, 12))

        ttk.Label(velocity_frame, text="Velocità [rad/s]:").grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=5
        )
        self.velocity_combo = ttk.Combobox(
            velocity_frame,
            textvariable=self.velocity_var,
            values=VELOCITY_OPTIONS,
            state="readonly",
            width=8,
        )
        self.velocity_combo.grid(row=0, column=1, sticky="w", pady=5)

        self.write_button = ttk.Button(
            velocity_frame, text="Scrivi velocità", command=self._write_velocity
        )
        self.write_button.grid(row=0, column=2, padx=(12, 0), pady=5)

        ttk.Label(velocity_frame, text="Valore INT32 scritto:").grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=5
        )
        ttk.Label(velocity_frame, textvariable=self.raw_velocity_var).grid(
            row=1, column=1, columnspan=2, sticky="w", pady=5
        )

        ttk.Label(main, textvariable=self.status_var, wraplength=550).pack(
            anchor="w", pady=(2, 0)
        )

        ttk.Label(
            main,
            text="Lettura automatica ogni 250 ms. Corrente in A stimata assumendo scala INT16 ±20 A. Chiudere la finestra per terminare.",
            foreground="#555555",
        ).pack(anchor="w", pady=(8, 0))

        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _release_connection(self):
        """Chiude, se possibile, il master precedente prima della riconnessione."""
        old_rpsoem = self.rpsoem
        self.rpsoem = None
        self.elac = None

        if old_rpsoem is None:
            return

        close_method = getattr(old_rpsoem, "close", None)
        if callable(close_method):
            try:
                close_method()
                return
            except Exception:
                pass

        for attribute_name in ("master", "_master", "ecat_master"):
            master = getattr(old_rpsoem, attribute_name, None)
            close_method = getattr(master, "close", None)
            if callable(close_method):
                try:
                    close_method()
                    return
                except Exception:
                    pass

    @staticmethod
    def _close_candidate(candidate):
        """Chiude una connessione appena creata ma non valida, se possibile."""
        close_method = getattr(candidate, "close", None)
        if callable(close_method):
            try:
                close_method()
                return
            except Exception:
                pass

        for attribute_name in ("master", "_master", "ecat_master"):
            master = getattr(candidate, attribute_name, None)
            close_method = getattr(master, "close", None)
            if callable(close_method):
                try:
                    close_method()
                    return
                except Exception:
                    pass

    def _try_reconnect(self, force=False):
        """Tenta periodicamente di ricreare il wrapper EtherCAT."""
        now = time.monotonic()

        if self.reconnect_in_progress:
            return
        if (
            not force
            and (now - self.last_reconnect_attempt) < RECONNECT_INTERVAL_S
        ):
            return

        self.last_reconnect_attempt = now
        self.reconnect_in_progress = True
        self.status_var.set("Slave non risponde: tentativo di riconnessione...")
        self._release_connection()

        try:
            candidate = RpPysoem()
            if candidate.ethercat_debug():
                self.rpsoem = candidate
                self.elac = candidate.node
                self.connected = True
                self.status_var.set("Riconnessione EtherCAT riuscita")
            else:
                self._close_candidate(candidate)
                self.connected = False
                self.status_var.set(
                    f"Slave non disponibile. Nuovo tentativo tra "
                    f"{RECONNECT_INTERVAL_S:.0f} s."
                )
        except Exception as error:
            self.connected = False
            self.status_var.set(
                f"Riconnessione fallita: {error}. Nuovo tentativo tra "
                f"{RECONNECT_INTERVAL_S:.0f} s."
            )
        finally:
            self.reconnect_in_progress = False

    def _refresh_values(self):
        if not self.connected or self.elac is None:
            self._try_reconnect()
        else:
            try:
                slow_raw = read_sdo_int32(self.elac, ANGLE_SLOW_INDEX)
                fast_raw = read_sdo_int32(self.elac, ANGLE_FAST_INDEX)
                voltage_raw = read_sdo_integer(
                    self.elac, DC_LINK_VOLTAGE_INDEX, byte_length=4, signed=False
                )
                current_raw = read_sdo_integer(
                    self.elac, CURRENT_ACTUAL_INDEX, byte_length=2, signed=True
                )
                error_field_raw = read_sdo_integer(
                    self.elac, ERROR_FIELD_INDEX, subindex=ERROR_FIELD_SUBINDEX,
                    byte_length=4, signed=False
                )

                slow_deg = normalize_angle_deg(slow_raw)
                fast_deg = normalize_angle_deg(fast_raw)
                voltage_v = voltage_from_raw(voltage_raw)
                current_a = current_from_raw_int16(current_raw)
                active_errors = decode_error_field(error_field_raw)

                self.slow_angle_var.set(f"{slow_deg:.2f}°  (raw INT32: {slow_raw})")
                self.fast_angle_var.set(f"{fast_deg:.2f}°  (raw INT32: {fast_raw})")
                self.dc_link_voltage_var.set(
                    f"{voltage_v:.3f} V  (raw UINT32: {voltage_raw})"
                )
                self.current_actual_var.set(
                    f"{current_a:.3f} A stimati  (raw INT16: {current_raw})"
                )
                self.error_field_raw_var.set(
                    f"0x{error_field_raw:08X}  ({error_field_raw})"
                )
                self.error_field_active_var.set(
                    ", ".join(active_errors) if active_errors else "Nessun bit di errore attivo"
                )
                self.last_update_var.set(
                    "Ultimo aggiornamento: "
                    + datetime.now().strftime("%H:%M:%S.%f")[:-3]
                )
                self.status_var.set("Connessione EtherCAT attiva - lettura SDO OK")
            except Exception as error:
                self.connected = False
                self.status_var.set(
                    f"Slave non risponde ({error}). Avvio riconnessione..."
                )
                self._try_reconnect()

        self.root.after(READ_INTERVAL_MS, self._refresh_values)

    def _write_velocity(self):
        try:
            if not self.connected or self.elac is None:
                raise ConnectionError(
                    "Slave EtherCAT non connesso. Attendere la riconnessione."
                )

            velocity = float(self.velocity_var.get())
            raw_value = write_target_velocity(self.elac, velocity)
            self.raw_velocity_var.set(str(raw_value))
            self.status_var.set(
                f"Comando inviato: {velocity:.1f} rad/s -> INT32 {raw_value}"
            )
        except Exception as error:
            # Un errore durante la scrittura può indicare una perdita di comunicazione.
            self.connected = False
            self.status_var.set("Scrittura fallita: verifico la connessione EtherCAT...")
            self._try_reconnect()
            messagebox.showerror("Errore scrittura velocità", str(error))

    def _close(self):
        self._release_connection()
        self.root.destroy()


def main():
    root = None
    try:
        rpsoem = RpPysoem()
        elac = getattr(rpsoem, "node", None)

        # Se lo slave non risponde all'avvio, apriamo comunque la GUI:
        # il timer proverà a riconnettersi periodicamente.
        try:
            connected = bool(rpsoem.ethercat_debug())
        except Exception:
            connected = False

        root = tk.Tk()
        EtherCATGui(root, rpsoem, elac, connected=connected)
        root.mainloop()
        return 0

    except Exception as error:
        try:
            if root is not None:
                messagebox.showerror("Errore EtherCAT", str(error))
            else:
                print(f"[ERROR] {error}")
        except tk.TclError:
            print(f"[ERROR] {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
