
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QComboBox,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QStackedWidget
)
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import QTimer
import sys
import subprocess

import os
import tempfile


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test selection")
        self.resize(480, 460)

        # Modalit di comunicazione (EtherCAT / CANopen)
        self.communication_mode = None

        # Variabili test
        # Test di posizione
        self.target_pos_1 = None
        self.target_pos_2 = None
        self.max_velocity = None
        # Test di velocit
        self.velocita = None
        self.tempo_test = None

        # Stato
        self.is_running = False
        self.current_process = None
        self.stop_flag_path = None

        # Layout principale
        root = QVBoxLayout(self)

        # ====== Sezione selezione comunicazione ======
        root.addWidget(QLabel("Communication selection mode:"))

        self.btn_eth = QPushButton("EtherCAT")
        self.btn_can = QPushButton("CANopen")
        self.btn_eth.clicked.connect(lambda: self.select_communication("EtherCAT"))
        self.btn_can.clicked.connect(lambda: self.select_communication("CANopen"))

        root.addWidget(self.btn_eth)
        root.addWidget(self.btn_can)

        # Label modalit selezionata
        self.mode_label = QLabel("No communication mode selected")
        root.addWidget(self.mode_label)

        # ====== Sezione selezione test ======
        root.addWidget(QLabel("Test type selection:"))
        self.combo = QComboBox()
        self.combo.addItems(["Poisition test", "Speed test"])
        root.addWidget(self.combo)

        
        self.proc_timer = QTimer(self)
        self.proc_timer.setInterval(500)  # ms
        self.proc_timer.timeout.connect(self._poll_process)


        # Stack parametri
        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        # Validatore numerico
        validator = QDoubleValidator(bottom=-1e12, top=1e12, decimals=6)

        # ========== Pagina: Test di posizione ==========
        page_pos = QWidget()
        pos_form = QFormLayout(page_pos)

        self.target_pos_1_input = QLineEdit()
        self.target_pos_1_input.setValidator(validator)
        self.target_pos_2_input = QLineEdit()
        self.target_pos_2_input.setValidator(validator)
        self.max_velocity_input = QLineEdit()
        self.max_velocity_input.setValidator(validator)

        pos_form.addRow("Target position 1:", self.target_pos_1_input)
        pos_form.addRow("Target position 2:", self.target_pos_2_input)
        pos_form.addRow("Max velocity [5-35rpm]:", self.max_velocity_input)

        # ========== Pagina: Test di velocit ==========
        page_vel = QWidget()
        vel_form = QFormLayout(page_vel)

        self.velocita_test_input = QLineEdit()
        self.velocita_test_input.setValidator(validator)
        self.tempo_test_input = QLineEdit()
        self.tempo_test_input.setValidator(validator)

        vel_form.addRow("Speed [5-35rpm]:", self.velocita_test_input)
        vel_form.addRow("Test duration [5-60s]:", self.tempo_test_input)

        self.stack.addWidget(page_pos)
        self.stack.addWidget(page_vel)

        self.combo.currentIndexChanged.connect(self.stack.setCurrentIndex)

        # ====== Pulsanti ======
        self.confirm = QPushButton("Start")
        self.confirm.clicked.connect(self.on_confirm)
        root.addWidget(self.confirm)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.on_stop)
        self.stop_btn.setEnabled(False)
        root.addWidget(self.stop_btn)

        # Etichetta stato
        self.status_label = QLabel("Ready")
        root.addWidget(self.status_label)

        # Disattiva tutto finché non si sceglie EtherCAT o CANopen
        self.enable_test_controls(False)

    # ==========================================================
    #              LANCIO SCRIPT ESTERNO CON PARAMETRI
    # ==========================================================
    
    def esegui_script_comunicazione(self, test_type, params):
        """
        Lancia lo script esterno (in base alla modalità selezionata)
        passando come primo argomento il tipo di test ('pos'/'vel')
        seguito dai parametri numerici.
        Inoltre passa via env una variabile STOP_FILE che lo script userà
        per sapere quando interrompersi in modo pulito.
        """
        if self.communication_mode == "EtherCAT":
            cmd = [sys.executable, "Test_Ethercat.py", test_type] + [str(p) for p in params]
        elif self.communication_mode == "CANopen":
            cmd = [sys.executable, "Test_CanOpen.py", test_type] + [str(p) for p in params]
        else:
            QMessageBox.warning(self, "Errore", "Communication mode not selected.")
            return

        # Crea uno stop-flag unico per questa esecuzione
        stop_name = f"stop_{test_type}_{int(QTimer().remainingTime())}_{os.getpid()}.flag"
        self.stop_flag_path = os.path.join(tempfile.gettempdir(), stop_name)
        try:
            # assicurati che non esista da run precedenti
            if os.path.exists(self.stop_flag_path):
                os.remove(self.stop_flag_path)
        except Exception:
            pass

        # Passa il path tramite variabile d'ambiente
        env = os.environ.copy()
        env["STOP_FILE"] = self.stop_flag_path

        print(f"[INFO] Avvio: {' '.join(cmd)}")
        print(f"[INFO] STOP_FILE: {self.stop_flag_path}")

        try:
            # Facoltativo: cattura stdout/stderr per log live (se vuoi mostrarli in GUI)
            self.current_process = subprocess.Popen(
                cmd,
                env=env,
                # stdout=subprocess.PIPE,
                # stderr=subprocess.STDOUT,
                # text=True,
            )
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile avviare lo script:\n{e}")




    
    def _check_range(self, value, minimo, massimo, nome_parametro):
        if value < minimo or value > massimo:
            QMessageBox.warning(
                self,
                "Errore parametro",
                f"{nome_parametro} must be within {minimo} and {massimo}."
            )
            return False
        return True
    # ==========================================================
    #              SELEZIONE COMUNICAZIONE
    # ==========================================================
    def select_communication(self, mode):
        self.communication_mode = mode
        self.mode_label.setText(f"Selected communication mode: {mode}")
        print(f"[INFO] Selected mode: {mode}")
        self.enable_test_controls(True)

        # Disabilita la scelta dopo la selezione
        self.btn_eth.setEnabled(False)
        self.btn_can.setEnabled(False)

    def enable_test_controls(self, enabled):
        self.combo.setEnabled(enabled)
        # Campi posizione
        self.target_pos_1_input.setEnabled(enabled)
        self.target_pos_2_input.setEnabled(enabled)
        self.max_velocity_input.setEnabled(enabled)
        # Campi velocit
        self.velocita_test_input.setEnabled(enabled)
        self.tempo_test_input.setEnabled(enabled)
        # Pulsante conferma
        self.confirm.setEnabled(enabled)

    # ==========================================================
    #                   AVVIO TEST (invio parametri)
    # ==========================================================
    
    def set_running(self, running: bool):
        self.is_running = running
        self.confirm.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        self.combo.setEnabled(not running)
        # Disattiva/attiva campi
        self.target_pos_1_input.setEnabled(not running)
        self.target_pos_2_input.setEnabled(not running)
        self.max_velocity_input.setEnabled(not running)
        self.velocita_test_input.setEnabled(not running)
        self.tempo_test_input.setEnabled(not running)

        if running:
            self.proc_timer.start()
        else:
            self.proc_timer.stop()


    def _parse_float(self, text: str):
        return float(text.strip().replace(",", "."))

    
    def on_confirm(self):
        if not self.communication_mode:
            QMessageBox.warning(self, "Errore", "Select first either EtherCAT or CANopen!")
            return

    # ===========================================
    #  TEST DI POSIZIONE
    # ===========================================
        if self.stack.currentIndex() == 0:
            # Lettura parametri
            t1 = self.target_pos_1_input.text()
            t2 = self.target_pos_2_input.text()
            mv = self.max_velocity_input.text()

            if not t1 or not t2 or not mv:
                QMessageBox.warning(self, "Errore", "Insert all input parameters (Position Test).")
                return

        # Conversione numerica
            try:
                self.target_pos_1 = self._parse_float(t1)
                self.target_pos_2 = self._parse_float(t2)
                self.max_velocity = self._parse_float(mv)
            except ValueError:
                QMessageBox.warning(self, "Errore", "Not numeric values (Position Test).")
                return

        # CHECK RANGE VELOCITÀ (535)
            if not self._check_range(self.max_velocity, 5, 35, "Max velocity"):
                return

        # ?? Regola richiesta: SOLO parametri del test di posizione
            self.esegui_script_comunicazione(
                "pos",
                [self.target_pos_1, self.target_pos_2, self.max_velocity])

            print("\n[TEST POSIZIONE] Parametri inviati allo script esterno")
            self.status_label.setText(f"Script ({self.communication_mode}) started for Position Test")

    # ===========================================
    #  TEST DI VELOCITa
    # ===========================================
        else:
            v = self.velocita_test_input.text()
            t = self.tempo_test_input.text()

            if not v or not t:
                QMessageBox.warning(self, "Errore", "Insert all input parameters (Speed Test).")
                return

        # Conversione numerica
            try:
                self.velocita = self._parse_float(v)
                self.tempo_test = self._parse_float(t)
            except ValueError:
                QMessageBox.warning(self, "Errore", "Not numeric values (Speed Test).")
                return

        # CHECK RANGE VELOCIT  (535)
            if not self._check_range(self.velocita, 5, 35, "Speed"):
                return

        # CHECK RANGE TEMPO (560)
            if not self._check_range(self.tempo_test, 5, 60, "Test Time"):
                return

        # ?? Regola richiesta: SOLO parametri del test di velocita
            self.esegui_script_comunicazione(
                "vel",
                [self.velocita, self.tempo_test]
        )

            print("\n[TEST VELOCIT] Parametri inviati allo script esterno")
            self.status_label.setText(f"Script ({self.communication_mode}) started for Speed Test")

    # Imposta stato di esecuzione
        self.set_running(True)

    # ==========================================================
    #                   STOP
    # ==========================================================

    
    
    def on_stop(self):
        print("[INFO] Interruzione richiesta dall'utente.")
        # 1) Attiva lo stop file (se presente)
        if self.stop_flag_path:
            try:
                with open(self.stop_flag_path, "w") as f:
                    f.write("STOP")
                print(f"[INFO] Stop file scritto: {self.stop_flag_path}")
            except Exception as e:
                print(f"[WARN] Non riesco a scrivere lo stop file: {e}")

        # 2) Attendi chiusura "gentile"
        if self.current_process is not None:
            try:
                self.current_process.wait(timeout=5)  # attendi fino a 5s
                print("[INFO] Processo terminato correttamente.")
            except Exception:
                print("[WARN] Timeout: termino il processo.")
                try:
                    self.current_process.terminate()
                    self.current_process.wait(timeout=2)
                    print("[INFO] Processo terminato (terminate).")
                except Exception as e:
                    print(f"[ERRORE] Non posso terminare il processo: {e}")
            finally:
                self.current_process = None

        # 3) Pulizia STOP_FILE lato GUI ✅
        self._remove_stop_file()

        # 4) Reset UI
        self.set_running(False)
        self.status_label.setText("Interrotto.")


    
    def _remove_stop_file(self):
        if self.stop_flag_path and os.path.exists(self.stop_flag_path):
            try:
                os.remove(self.stop_flag_path)
                print(f"[INFO] STOP_FILE rimosso: {self.stop_flag_path}")
            except Exception as e:
                print(f"[WARN] Impossibile rimuovere STOP_FILE: {e}")
        self.stop_flag_path = None

    
    def _poll_process(self):
        if self.current_process is None:
            return
        ret = self.current_process.poll()
        if ret is not None:
            # Processo terminato
            self.current_process = None
            self._remove_stop_file()  # ✅ rimuove STOP_FILE quando il figlio e finito
            self.set_running(False)
            self.status_label.setText(f"Terminato (exit code {ret}).")



def main():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()