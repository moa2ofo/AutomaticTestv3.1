# Generatore `cia402.c` / `cia402.h`

## File

- `generate_cia402.py`: generatore Python, usa solo la standard library.
- `cia402.c`: sorgente generato partendo da `cia402appl.c`.
- `cia402.h`: header generato partendo da `cia402appl.h`.
- `cia402_generation_report.txt`: elenco degli oggetti inclusi, esclusi e degli avvisi.

## Esecuzione

```bash
python3 generate_cia402.py \
  --eds edsCia402Obj.txt \
  --template-c cia402appl.c \
  --template-h cia402appl.h \
  --out-c cia402.c \
  --out-h cia402.h \
  --report cia402_generation_report.txt
```

Per gli oggetti `rw` con `PDOMapping=1`, il comportamento predefinito segue l'esempio Beckhoff e abilita il mapping RxPDO. Per consentire sia RxPDO sia TxPDO:

```bash
--rw-pdo-direction both
```

## Oggetti inclusi per impostazione predefinita

- Mapping PDO `0x1600–0x17FF` e `0x1A00–0x1BFF`.
- Oggetti manufacturer-specific `0x2000–0x5FFF`.
- Oggetti di profilo `0x6000–0x67FF`.
- `0x605C`, anche se non presente nell'EDS, perché è usato dalla state machine Beckhoff fornita come template.

Gli oggetti di comunicazione CANopen `0x1000–0x1FFF`, esclusi i mapping PDO sopra indicati, non vengono importati automaticamente: nell'EtherCAT Slave Stack molti sono già gestiti dallo stack o sono sostituiti da oggetti EtherCAT/CoE. L'opzione `--include-communication` esiste, ma va usata solo dopo una verifica dei conflitti con l'object dictionary SSC.

## Cosa viene generato

Lo script rigenera:

- typedef per ARRAY/RECORD dell'EDS;
- struttura `CiA402Objects`;
- descrittori `TSDOINFOENTRYDESC` e nomi SDO;
- `DefCiA402ObjectValues`;
- `DefCiA402AxisObjDic`;
- associazioni `pVarPtr` nello `switch` di `CiA402_Init()`.

La state machine, le funzioni di mapping applicativo e il dummy motion controller restano quelli del file di esempio.

## Limite funzionale

Gli oggetti aggiunti sono disponibili nell'object dictionary e dispongono della relativa memoria applicativa. Lo script non implementa automaticamente il significato funzionale di ogni oggetto: per esempio regolatori, homing, interpolazione e oggetti manufacturer-specific devono essere collegati alla logica reale del firmware.

Il file EDS contiene quattro mapping PDO, mentre la logica applicativa dell'esempio Beckhoff gestisce esplicitamente i profili/mapping originari. Se si usa `0x1603` o `0x1A03` con dati reali, occorre estendere anche `APPL_GenerateMapping`, `APPL_InputMapping` e `APPL_OutputMapping` in base al layout desiderato.

## Verifiche eseguite

- compilazione Python del generatore con `py_compile`;
- controllo statico della presenza di ogni oggetto in header, dictionary e switch C;
- compilazione sintattica dell'header generato con un set minimo di tipi e macro SSC simulati.

La compilazione completa del progetto richiede gli header e la configurazione reali del Beckhoff EtherCAT SSC usati nel firmware.
