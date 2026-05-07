# Utilizzo degli script Python

## Configurazione ambiente virtuale (Opzionale)

È consigliato utilizzare un ambiente virtuale Python per isolare le dipendenze del progetto.

**Su Windows:**

1. Aprire il prompt dei comandi nella directory principale del progetto
2. Creare l'ambiente virtuale:

   ``` shell
   python -m venv .venv
   ```

3. Attivare l'ambiente virtuale:

   ``` shell
   .venv\Scripts\activate
   ```

4. Installare le dipendenze:

   ``` shell
   pip install pysoem canopen
   ```

5. Per disattivare l'ambiente virtuale quando si ha finito:

   ``` shell
   deactivate
   ```

---

## Setup Hardware

### EtherCAT

- Collegare la porta 0 della board (configurazione hardware EtherCAT) alla porta Ethernet del PC tramite un cavo Ethernet diretto
- La board deve essere configurata con firmware/hardware EtherCAT

### CANopen

- Collegare la porta 0 della board (configurazione firmware/hardware CAN) ad un adattatore USB-to-CAN
- Collegare l'adattatore USB al PC
- Aggiungere una resistenza di terminazione da 60Ω sul bus CAN come previsto dallo standard
- Hardware testato: IXXAT USB-to-CAN adapter

---

## Procedura di utilizzo

### Setup EtherCAT

1. Se si utilizza un ambiente virtuale, assicurarsi che sia attivato prima di eseguire gli script
2. Eseguire lo script `00_find_adapters.py` per ottenere la lista dei dispositivi di rete disponibili
3. Identificare l'adattatore Ethernet al quale è collegato lo slave EtherCAT
4. Copiare il nome dell'adattatore (esempio: `\Device\NPF_{3CD8763A-B408-4140-A249-D71C2E41AD82}`)
5. Sostituire il valore della variabile `ifname` nel file `ecat_common_func.py`, riga 6
6. Nel file `01_run_tests.py`, assicurarsi che le righe per EtherCAT siano decommentate e quelle per CANopen commentate:

   ```python
   # use this lines for ethercat testing
   rpsoem = RpPysoem()
   elac = rpsoem.node
   
   # use this lines for canopen testing
   # network = initCANopen()
   # for node_id in network:
   #     if node_id == 1:
   #         elac = network[node_id]
   ```

7. Eseguire lo script `01_run_tests.py`

### Setup CANopen

1. Se si utilizza un ambiente virtuale, assicurarsi che sia attivato prima di eseguire gli script
2. Verificare che l'adattatore USB-to-CAN sia correttamente collegato
3. Nel file `01_run_tests.py`, assicurarsi che le righe per CANopen siano decommentate e quelle per EtherCAT commentate:

   ```python
   # use this lines for ethercat testing
   # rpsoem = RpPysoem()
   # elac = rpsoem.node
   
   # use this lines for canopen testing
   network = initCANopen()
   for node_id in network:
       if node_id == 1:
           elac = network[node_id]
   ```

4. Eseguire lo script `01_run_tests.py`

---

Lo script principale eseguirà automaticamente, in sequenza, quattro test:

### 1. Test Homing 37

Esegue la procedura di homing utilizzando il metodo 37 (CiA 402 standard). Il drive aggiorna il suo "zero" di posizione con quello attuale.

### 2. Test Profile Position

Verifica il controllo di posizione del drive. Il motore si muove ciclicamente tra due posizioni target predefinite (P1 e P2), utilizzando i parametri di velocità e accelerazione configurati.

### 3. Test Profile Velocity

Testa il controllo di velocità del drive. Il motore viene portato a una velocità target e poi fermato, ripetendo il ciclo più volte per verificare la corretta gestione delle rampe di accelerazione e decelerazione.

### 4. Test Profile Torque

Valida il controllo di coppia del drive. Viene applicata una coppia al motore e lasciato libero di ruotare misurando la resistenza applicata dal carico.

---

## Dizionario Oggetti CiA 402 Utilizzati

Per una descrizione completa del dizionario si rimanda al deliverable _D-07-C121-0230-Controllo Motore.pdf_ e alla normativa _CEI EN 61800-7-201 2016_.

### Controllo e Stato

**0x6040 - Controlword**: Registro di controllo per l'invio di comandi al drive (shutdown, switch on, enable operation, fault reset, homing start, etc.).

**0x6041 - Statusword**: Registro di stato che riflette le condizioni operative del drive secondo la macchina a stati DS402 (ready to switch on, switched on, operation enabled, fault, target reached, homing attained, etc.).

**0x6060 - Modes of Operation**: Selezione modalità operativa (1=Profile Position, 3=Profile Velocity, 4=Profile Torque, 6=Homing).

### Parametri di Posizione

**0x6064 - Position Actual Value**: Valore di posizione attuale (read-only).

**0x607A - Target Position**: Posizione target per modalità Profile Position.

**0x607C - Home Offset**: Offset applicato alla posizione di riferimento dopo la procedura di homing.

### Parametri di Velocità

**0x607F - Max Profile Velocity**: Limite superiore di velocità per i profili di movimento.

**0x6081 - Profile Velocity**: Velocità target per i movimenti in modalità Profile Position.

**0x60FF - Target Velocity**: Velocità target per modalità Profile Velocity.

**0x606D - Velocity Window**: Finestra di tolleranza per considerare raggiunta la velocità target.

**0x606E - Velocity Window Time**: Tempo minimo di permanenza nella velocity window per confermare il raggiungimento.

**0x606F - Velocity Threshold**: Soglia per rilevare l'avvicinamento alla velocità target.

**0x6070 - Velocity Threshold Time**: Tempo di permanenza nella velocity threshold.

### Parametri di Accelerazione

**0x6083 - Profile Acceleration**: Accelerazione per i profili di movimento.

**0x6084 - Profile Deceleration**: Decelerazione per i profili di movimento.

### Parametri di Coppia

**0x6071 - Target Torque**: Coppia target espressa in per-mille della coppia nominale.

**0x6072 - Max Torque**: Limite superiore di coppia (protezione meccanica).

**0x6074 - Torque Demand**: Coppia richiesta istantanea al drive (read-only).

**0x6087 - Torque Slope**: Rampa di variazione della coppia (rate of change in per-mille/s).

### Parametri di Corrente

**0x6073 - Max Current**: Corrente massima ammessa per il motore (protezione elettrica).

**0x6075 - Motor Rated Current**: Corrente nominale del motore specificata dal costruttore.

### Parametri di Homing

**0x6098 - Homing Method**: Metodo di homing secondo CiA 402 (nel progetto: metodo 37).

### Parametri di Trasmissione Meccanica

**0x6091 - Gear Ratio**:

- Subindex 1: numero di giri motore (numeratore)
- Subindex 2: numero di giri albero uscita (denominatore)

**0x6092 - Feed Constant**: Costante per la conversione rotazione-traslazione (Subindex 1: feed per rivoluzione).

---

## Note

- usare solamente la porta 0 del dispositivo per ethercat
- in caso di errore, resettare il chip prima di rieseguire gli script.
- Per l'utilizzo della libreria pysoem è consigliato utilizzare un PC con una scheda di rete performante, in grado di supportare correttamente la comunicazione EtherCAT.
- Nel collegamento tra il PC e lo slave EtherCAT è raccomandato l'utilizzo di un cavo Ethernet di alta qualità.
- L'utilizzo di hardware non adeguato (PC o cavi economici) può causare perdite di comunicazione durante l'esecuzione degli script. In particolare, potrebbero verificarsi errori di WckError o PacketError, anche se sporadicamente.
# AutomaticTestv3.1
