# Integrazione PLC NJ con Bilancia IDECON
## Protocollo TCP/IP e Architettura Comunicazione

**Versione:** 1.0  
**Data:** 2026-02-10  
**Stato:** Testato e Validato

---

## 1. Overview Architettura

### 1.1 Schema Comunicazione

```
┌─────────────┐      OPC UA/TCPIP      ┌─────────────┐      TCP/IP      ┌─────────────┐
│    SCADA    │  ←──────────────────→  │    PLC NJ   │  ←────────────→  │   IDECON    │
│  (Linea/Flow│                        │  (Sysmac    │    STX/CMD/ETX   │ (Pesatrice) │
│   Pack)     │                        │   Studio)   │                  │             │
└─────────────┘                        └─────────────┘                  └─────────────┘
      ↓                                       ↓                                ↓
- RecipeIndex                          - Gestione comandi                  - Pesi
- ProductionOrder                      - Parsing risposte                  - Statistiche  
- BatchCode                            - State Machine                     - Eventi
- ProductionInfo                       - Buffer dati                       - Allarmi
```

### 1.2 Modalità Operative

La bilancia IDECON supporta tre modalità operative (STATSV posizione 7):

| Modalità | Codice | Comandi Disponibili | Note |
|----------|--------|---------------------|------|
| **LOCAL** | 1 | BATCHSTART, BATCHSTOP, dati | Solo gestione batch, NO start/stop nastri |
| **REMOTE** | 2 | TUTTI i comandi incl. START/STOP | Controllo completo da PLC |
| **MAINTENANCE** | 3 | Diagnostica | Solo manutenzione |

**IMPORTANTE:** Per sicurezza, la modalità REMOTE richiede che l'operatore imposti manualmente la bilancia in REMOTE dal pannello HMI. Il PLC può verificare la modalità ma non forzarla.

### 1.3 Flusso Operativo Standard (LOCAL Mode)

```
1. SCADA invia: RecipeIndex + ProductionData
2. PLC mappa RecipeIndex → RecipeName (es. "225g")
3. PLC invia a IDECON: BATCHMODIFY campi
4. Operatore su HMI bilancia: imposta REMOTE mode
5. Operatore su HMI bilancia: START produzione
6. IDECON invia: WEIGHT, STATP, EVENT automatici
7. A fine lotto: Operatore STOP + BATCHSTOP
8. PLC riceve statistiche finali
```

---

## 2. Protocollo TCP/IP

### 2.1 Formato Messaggi

Ogni comando/risposta è incapsulato:

```
<STX>COMANDO<ETX>
<STX>COMANDO=VALORE<ETX>
<STX>COMANDO=VAL1|VAL2|...|VALn<ETX>
```

Dove:
- **STX** (0x02): Start of Text
- **ETX** (0x03): End of Text
- **|=** (0x7C, 0x3D): Separatori dati

### 2.2 Configurazione Socket

```
IP: 172.16.224.210 (configurabile)
Port: 50000 (configurabile)
Timeout connessione: 10s
Timeout ricezione: 5s
Keep-alive: Abilitato
```

### 2.3 MSGFILTER - Controllo Notifiche

Bitmask per abilitare messaggi automatici:

| Bit | Valore | Descrizione | Uso Tipico |
|-----|--------|-------------|------------|
| 0 | 1 | Risposte comandi | SEMPRE |
| 1 | 2 | Errori | SEMPRE |
| 2 | 4 | Eventi | SEMPRE |
| 3 | 8 | Statistiche | Se ENABLESTATS |
| 4 | 16 | Pesi individuali | IN PRODUZIONE |
| 5 | 32 | Messaggi importanti | RARO |

**Valori consigliati:**
- Produzione attiva: `MSGFILTER=23` (1+2+4+16)
- Solo monitoraggio: `MSGFILTER=7` (1+2+4)
- Tutto attivo: `MSGFILTER=63` (1+2+4+8+16+32)

---

## 3. Comandi PLC → IDECON

### 3.1 Comandi Base (Tutte le Modalità)

| Comando | Sintassi | Risposta | Descrizione |
|---------|----------|----------|-------------|
| STATSV | `STATSV` | `STATSV=XXXXXXXX` | Stato macchina 8 posizioni |
| ERRNUM | `ERRNUM` | `ERRNUM=N` | Codice errore attivo (0=nessuno) |
| LINECODE | `LINECODE` | `LINECODE=xxx` | Codice linea configurata |
| DATETIME | `DATETIME` | `DATETIME=gg/mm/aaaa	hh:mm:ss.mmm` | Data/ora bilancia |
| BATCHINFO | `BATCHINFO` | `BATCHINFO=...` | Configurazione batch |

**Dettaglio STATSV (8 posizioni):**
```
Pos 1: Stato motori (0=Fermo, 1=Regolazione, 2=Pronto, 3=Standby, 4=Ripresa)
Pos 2: Produzione (0=OFF, 1=ON)
Pos 3: Errori (0=No, 1=Sì)
Pos 4: Warnings (0=No, 1=Sì)
Pos 5: Messaggi (0=No, 1=Sì)
Pos 6: Statistiche abilitate (0=No, 1=Sì)
Pos 7: Modalità (1=Local, 2=Remote, 3=Maintenance)
Pos 8: Stato connessione
```

### 3.2 Comandi Batch (LOCAL e REMOTE)

| Comando | Sintassi | Quando Usare |
|---------|----------|--------------|
| BATCHSTART | `BATCHSTART` | Apre nuovo lotto (da HMI) |
| BATCHSTOP | `BATCHSTOP` | Chiude lotto attivo (da HMI) |
| BATCHMODIFY | `BATCHMODIFY=CAMPO|VALORE` | Prima di BATCHSTART |

**Campi BATCHMODIFY:**
- `OPERATOR` - Nome operatore
- `BATCHCODE` - Codice lotto/batch
- `PRODUCTIONORDER` - Ordine produzione
- `EXTRAFIELD1` - Campo libero 1
- `EXTRAFIELD2` - Campo libero 2

**Esempio sequenza:**
```
BATCHMODIFY=PRODUCTIONORDER|ORD2024001
BATCHMODIFY=BATCHCODE|LOTTO_A_001
BATCHMODIFY=EXTRAFIELD1|TURNO_MATTINA
BATCHMODIFY=EXTRAFIELD2|LINEA_01
BATCHSTART
```

### 3.3 Comandi Produzione (SOLO REMOTE Mode)

⚠️ **ATTENZIONE:** Questi comandi richiedono che la bilancia sia in modalità REMOTE (STATSV pos 7 = 2)

| Comando | Sintassi | Descrizione | Sicurezza |
|---------|----------|-------------|-----------|
| START | `START` | Avvia nastri | Verificare protezioni fisiche |
| STOP | `STOP` | Ferma nastri | Sempre sicuro |

**Nota:** Se inviato in LOCAL mode, la risposta è:
```
START is possibile only in remote modality
```

### 3.4 Comandi Statistiche

| Comando | Sintassi | Descrizione |
|---------|----------|-------------|
| ENABLESTATS | `ENABLESTATS` | Abilita invio automatico STATP |
| DISABLESTATS | `DISABLESTATS` | Disabilita invio |
| STATCADENCY | `STATCADENCY=[sec]` | Frequenza invio (default 60s) |
| STATREQ | `STATREQ` | Richiesta immediata STATP |
| STATREQATB | `STATREQATB` | Richiesta STATPATB |
| SELSTATSANSWER | `SELSTATSANSWER=STATP/STATPATB` | Seleziona formato |

### 3.5 Comandi Diagnostica e Messaggi

| Comando | Sintassi | Descrizione | Supporto |
|---------|----------|-------------|----------|
| RESETERRORI | `RESETERRORI` | Azzera errori attivi | 12", 7" |
| SHOWMESSAGE | `SHOWMESSAGE=[testo]` | Mostra su display HMI | 12" only |
| SHOWMESSAGE | `SHOWMESSAGE=` | Rimuove messaggio | 12" only |
| GETRECIPELIST | `GETRECIPELIST` | Lista ricette disponibili | 12" only |
| GET_CURRENT_PIECE_STAT | `GET_CURRENT_PIECE_STAT=N|M|POS` | Media ultimi pezzi | 12" only |

---

## 4. Messaggi IDECON → PLC (Notifiche)

### 4.1 WEIGHT - Pesata Individuale

**Trigger:** Ad ogni prodotto pesato (se MSGFILTER bit 4 = 1)

**Formato:**
```
WEIGHT=timestamp|order|batch|recipe|line|serial|weight_mg|delta_mg|classification|
```

**Esempio:**
```
WEIGHT=2026.02.10 14:32:42:773|ORD001|BATCH001|225g|Linea1|ID02792|224700|700|20480|
```

**Campi:**
| Pos | Campo | Tipo | Descrizione |
|-----|-------|------|-------------|
| 1 | timestamp | STRING | Data/ora pesata |
| 2 | order | STRING | Ordine produzione |
| 3 | batch | STRING | Codice batch |
| 4 | recipe | STRING | Nome ricetta |
| 5 | line | STRING | Codice linea |
| 6 | serial | STRING | Serial number bilancia |
| 7 | weight_mg | DINT | Peso in milligrammi |
| 8 | delta_mg | DINT | Delta da nominale in mg |
| 9 | classification | UDINT | Bitmap 19 bit |

**Classification Bitmap (19 bit):**
```
Bit 0:  Product too long
Bit 1:  Product too short
Bit 2:  Metal detected
Bit 3:  Weight ++ category
Bit 4:  Weight + category
Bit 5:  Weight -- category
Bit 6:  Weight - category
Bit 7:  Weight OK category
Bit 8:  Expelled (scartato)
Bit 9:  Product too close
Bit 10: New dynamic tare
Bit 11: Incorrect tare
Bit 12: Above max capacity
Bit 13: Below min capacity
Bit 14: OK- category accepted
Bit 15: No upstream consent
Bit 16: Invalid pre-weight
Bit 17: OK above nominal
Bit 18: OK below nominal
```

**Valori tipici:**
- `0x80` (128): OK
- `0x20480` (132224): OK + OK+
- `0x10080` (65664): OK + OK-
- `0x10` (16): + category
- `0x100` (256): EXPELLED
- `0x120` (288): -- + EXPELLED

### 4.2 STATP - Statistiche Batch (50 campi)

**Trigger:** Ogni STATCADENCY secondi se ENABLESTATS attivo

**Formato:**
```
STATP=field1|field2|...|field50|
```

**Campi principali:**

| Pos | Campo | Descrizione |
|-----|-------|-------------|
| 1 | DateTime | Timestamp |
| 2 | BatchStart | Inizio batch |
| 3 | ProductionOrder | Ordine |
| 4 | ProductionCode | Codice prodotto |
| 5 | RecipeName | Nome ricetta |
| 6 | LineCode | Linea |
| 7 | SerialNumber | Serial |
| 8 | TotalProducts | Totale pezzi |
| 9 | TotalAccepted | Accettati |
| 10 | AvgWeight | Peso medio |
| 11 | MinWeight | Peso min |
| 12 | MaxWeight | Peso max |
| 13-18 | Rejected | Scartati per categoria (--, -, +, ++) |
| 27-46 | Incremental | Dati incrementali |
| 50 | StdDeviation | Deviazione standard |

### 4.3 EVENT - Eventi ed Errori

**Trigger:** Eventi macchina (se MSGFILTER bit 2 = 1)

**Formato:**
```
EVENT=timestamp|order|batch|recipe|line|serial|Cod.Evento|Descrizione|Operatore|
```

**Codici Evento principali:**

| Codice | Nome | Descrizione |
|--------|------|-------------|
| 1000 | Errors Reset | Azzeramento errori |
| 1001 | Recipe Change | Cambio ricetta |
| 1004 | Batch Opening | Apertura lotto |
| 1005 | Batch Closure | Chiusura lotto |
| 1006 | Batch Change | Cambio lotto |
| 1007 | Modified Batch | Modifica lotto |
| 1008 | Command Not Recognized | Comando non riconosciuto |
| 1011 | Not Remote Mode | Comando remoto rifiutato (non in remote) |
| 1012 | Mode Change | Cambio modalità (Local/Remote/Maintenance) |
| 30 | Error 30 | Negative Mean Error |

---

## 5. Sequenze Operative Complete

### 5.1 Sequenza Standard: Avvio Nuova Produzione

**Precondizioni:**
- Bilancia in LOCAL mode (default)
- Batch chiuso
- Macchina ferma

```
FASE 1: Configurazione Dati (LOCAL Mode)
─────────────────────────────────────────
1. PLC riceve da SCADA:
   - RecipeIndex (es. 5)
   - ProductionOrder (es. "ORD2024001")
   - BatchCode (es. "LOTTO_A_001")
   - ProductionInfo (es. "TURNO_MATTINA")
   - Quantity (es. 1000)

2. PLC mappa RecipeIndex → RecipeName (es. "225g")

3. PLC invia a IDECON:
   → BATCHMODIFY=PRODUCTIONORDER|ORD2024001
   → BATCHMODIFY=BATCHCODE|LOTTO_A_001
   → BATCHMODIFY=EXTRAFIELD1|TURNO_MATTINA
   → BATCHMODIFY=EXTRAFIELD2|1000

4. Verifica:
   ← BATCHINFO (conferma dati scritti)

FASE 2: Attesa Operatore (LOCAL Mode)
──────────────────────────────────────
5. Operatore su HMI bilancia:
   - Verifica dati lotto
   - Imposta REMOTE mode (se abilitato)
   - Preme START produzione

ALTERNATIVA A (LOCAL Mode - Consigliato):
──────────────────────────────────────────
6a. Operatore avvia da HMI bilancia
7a. PLC riceve EVENT=1004 (Batch Opening)
8a. PLC riceve EVENT=1012 (Remote connection)
9a. Bilancia invia automaticamente WEIGHT/STATP

ALTERNATIVA B (REMOTE Mode - Opzionale):
─────────────────────────────────────────
6b. PLC verifica: STATSV pos 7 = 2 (REMOTE)
7b. PLC invia: BATCHSTART
8b. PLC attende: EVENT=1004
9b. PLC invia: ENABLESTATS + STATCADENCY=30
10b. PLC invia: MSGFILTER=23
11b. PLC invia: START (solo se REMOTE)

FASE 3: Produzione Attiva
──────────────────────────
12. PLC riceve continuamente:
    ← WEIGHT (ogni prodotto)
    ← STATP (ogni 30s)
    ← EVENT (eventi/errori)

13. PLC polling ogni 5s:
    → STATSV (verifica stato)
```

### 5.2 Sequenza: Chiusura Lotto

```
FASE 1: Richiesta Chiusura
───────────────────────────
1. Operatore preme "Chiudi Lotto" su HMI

FASE 2: Arresto (LOCAL o REMOTE)
─────────────────────────────────
2a. Se LOCAL: Operatore ferma da HMI bilancia
2b. Se REMOTE: PLC invia STOP

3. Attesa stop nastri (STATSV pos 1 = 0)

FASE 3: Chiusura Batch
───────────────────────
4. PLC invia: BATCHSTOP
5. PLC riceve: EVENT=1005 (Batch Closure)

FASE 4: Raccolta Dati Finali
─────────────────────────────
6. PLC invia: STATREQ (statistiche finali)
7. PLC riceve: STATP completo
8. PLC salva su DB/SCADA:
   - Totale pezzi
   - Media/min/max pesi
   - Scartati per categoria
   - Deviazione standard

FASE 5: Reset
──────────────
9. PLC invia: DISABLESTATS
10. Opzionale: BATCHSTART per nuovo lotto
```

### 5.3 Sequenza: Gestione Errore 30 (Negative Mean Error)

```
1. PLC riceve: EVENT con Codice 30
   Descrizione: "Negative mean error"

2. Log immediato evento

3. Verifica condizioni:
   - Media pesi < Peso nominale
   - Durata > Negative mean error delay time

4. Opzioni gestione:
   
   OPZIONE A - Ignora (se configurato):
   - Continua produzione
   - Log warning
   
   OPZIONE B - Reset errore:
   → RESETERRORI
   - Log azione
   
   OPZIONE C - Reset completo:
   → STOP
   → BATCHSTOP
   → BATCHSTART (nuovo batch, statistiche azzerate)
   → START (se REMOTE)
   
   OPZIONE D - Notifica operatore:
   - Attesa intervento manuale
   - Possibile cambio ricetta
```

### 5.4 Sequenza: Cambio Ricetta da SCADA

```
1. SCADA invia: RecipeChangeRequest
   - RecipeIndex: 3 (esempio)
   - ProductionOrder: "ORD2024002"
   - ecc.

2. PLC verifica: FLAG.RunCycle = FALSE (non in produzione)

3. PLC mappa: RecipeIndex 3 → "450g"

4. Se LOCAL mode:
   - PLC invia solo BATCHMODIFY campi
   - Messaggio su display: "Cambiare ricetta a 450g"
   - Operatore cambia manualmente da HMI bilancia
   
   Se REMOTE mode:
   - PLC invia: RECIPE=450g
   - PLC verifica risposta

5. Conferma a SCADA: RecipeChangeOK
```

---

## 6. Mapping Dati SCADA ↔ PLC ↔ IDECON

### 6.1 Struttura Dati SCADA → PLC

| Dato SCADA | Tipo | Var PLC | Descrizione |
|------------|------|---------|-------------|
| RecipeIndex | INT | G_Scada_RecipeIndex | Indice 1-30 |
| RecipeChangeRequest | BOOL | G_Scada_RecipeChangeReq | Richiesta cambio |
| ProductionOrder | STRING[64] | G_Scada_Order | Ordine cliente |
| BatchCode | STRING[64] | G_Scada_Batch | Codice lotto |
| ProductionInfo | STRING[64] | G_Scada_Info | Info aggiuntive |
| Quantity | DINT | G_Scada_Qty | Quantità prevista |
| ProductionChangeRequest | BOOL | G_Scada_ProdChangeReq | Richiesta cambio prod |

### 6.2 Mapping RecipeIndex → RecipeName

| RecipeIndex | RecipeName IDECON | Peso Nominale |
|-------------|-------------------|---------------|
| 1 | 225g | 225g |
| 2 | 450g | 450g |
| 3 | 900g | 900g |
| ... | ... | ... |

*Nota: Configurare array di mapping nel PLC*

### 6.3 Mapping Campi → IDECON

| Campo SCADA | Campo IDECON | Comando | Esempio |
|-------------|--------------|---------|---------|
| ProductionOrder | PRODUCTIONORDER | BATCHMODIFY | ORD2024001 |
| BatchCode | BATCHCODE | BATCHMODIFY | LOTTO_A_001 |
| ProductionInfo | EXTRAFIELD1 | BATCHMODIFY | TURNO_MATTINA |
| Quantity | EXTRAFIELD2 | BATCHMODIFY | 1000 |
| RecipeName | Recipe (in WEIGHT) | RECIPE* | 225g |

*RECIPE solo se REMOTE mode

### 6.4 Dati IDECON → PLC → SCADA

| Dato IDECON | Var PLC | Tipo | Destinazione SCADA |
|-------------|---------|------|-------------------|
| WEIGHT.weight_mg | G_Idecon_LastWeight.WeightMg | DINT | Peso reale |
| WEIGHT.delta_mg | G_Idecon_LastWeight.DeltaMg | DINT | Scarto |
| WEIGHT.classification | G_Idecon_LastWeight.Classification | UDINT | Stato prodotto |
| STATP.TotalProducts | G_Idecon_BatchStats.TotalProducts | UDINT | Contatore totale |
| STATP.TotalAccepted | G_Idecon_BatchStats.AcceptedProducts | UDINT | Contatore OK |
| STATP.AvgWeight | G_Idecon_BatchStats.AverageWeight_g | REAL | Media peso |
| EVENT.event_code | G_Idecon_LastEvent.Code | UINT | Eventi/Allarmi |

---

## 7. Gestione Errori e Timeout

### 7.1 Tabella Errori Comuni

| Errore | Causa | Gestione PLC |
|--------|-------|--------------|
| Timeout connessione | Bilancia offline | Riprova ogni 10s, allarme dopo 3 tentativi |
| Timeout comando | Risposta mancante | Riprova 3 volte, poi segnala errore |
| REFUSED | Comando non accettato | Log errore, verifica stato macchina |
| ERRNUM=30 | Negative Mean Error | Vedi sequenza §5.3 |
| ERRNUM=3 | Generic error | RESETERRORI o analisi da HMI |
| "Not in remote" | Comando START in LOCAL | Log warning, richiede intervento operatore |
| "Batch already open" | BATCHSTART su batch aperto | Ignora o BATCHSTOP prima |

### 7.2 Timeout Consigliati

| Operazione | Timeout | Azione su Timeout |
|------------|---------|-------------------|
| Connessione TCP | 10s | Retry |
| Invio comando | 5s | Retry (max 3) |
| Ricezione STATP | 3s | Richiesta esplicita STATREQ |
| Ricezione EVENT | - | Asincrono, no timeout |
| Chiusura batch | 5s | Verifica con STATSV |

### 7.3 Stati Errore G_System_Error

```
G_System_Error := TRUE quando:
- Timeout connessione (>3 tentativi)
- Errore parsing risposta
- Errore grave bilancia (ERRNUM > 0 persistente)
- Discordanza statistiche (STATP vs conteggi interni)
- Modalità non coerente (richiesta REMOTE ma in LOCAL)

Reset:
- Comando RESETERRORI eseguito
- Connessione ripristinata
- Acknowledge operatore
```

---

## 8. Implementazione Codice ST

### 8.1 Function Block: FB_IDECON_Client

```iecst
FUNCTION_BLOCK FB_IDECON_Client
VAR_INPUT
    Execute     : BOOL;          // Esegui comando
    Command     : STRING[255];   // Comando da inviare
    Timeout     : TIME := T#5S;  // Timeout risposta
END_VAR

VAR_OUTPUT
    Done        : BOOL;          // Comando completato
    Busy        : BOOL;          // In esecuzione
    Error       : BOOL;          // Errore
    ErrorID     : WORD;          // Codice errore
    Response    : STRING[512];   // Risposta ricevuta
END_VAR

VAR_IN_OUT
    Socket      : _sSOCKET;      // Socket TCP
END_VAR

VAR
    State       : INT;           // Stato FSM
    Timer       : TON;           // Timer timeout
    SendBuf     : ARRAY[0..511] OF BYTE;
    RecvBuf     : ARRAY[0..511] OF BYTE;
    CmdLen      : UINT;
    RetryCount  : INT;
END_VAR

// Stati FSM
// 0: Idle
// 1: Prepare
// 2: Send STX
// 3: Send Command
// 4: Send ETX
// 5: Wait Response
// 6: Parse Response
// 7: Done/Error
```

### 8.2 Struttura Dati: Idecon_WeightData

```iecst
TYPE Idecon_WeightData :
STRUCT
    // Dati base
    Timestamp           : STRING[32];    // Data/ora pesata
    ProductionOrder     : STRING[64];    // Ordine
    BatchCode           : STRING[64];    // Batch
    RecipeName          : STRING[32];    // Ricetta
    LineCode            : STRING[32];    // Linea
    SerialNumber        : STRING[16];    // Serial
    
    // Valori numerici
    WeightMg            : DINT;          // Peso mg
    DeltaMg             : DINT;          // Delta mg
    Classification      : UDINT;         // Bitmap 19 bit
    
    // Flag decodificati (19 bit)
    FlagProductTooLong  : BOOL;          // Bit 0
    FlagProductTooShort : BOOL;          // Bit 1
    FlagMetal           : BOOL;          // Bit 2
    FlagWeightPP        : BOOL;          // Bit 3
    FlagWeightP         : BOOL;          // Bit 4
    FlagWeightMM        : BOOL;          // Bit 5
    FlagWeightM         : BOOL;          // Bit 6
    FlagWeightOK        : BOOL;          // Bit 7
    FlagExpelled        : BOOL;          // Bit 8
    FlagProductTooClose : BOOL;          // Bit 9
    FlagNewDynamicTare  : BOOL;          // Bit 10
    FlagIncorrectTare   : BOOL;          // Bit 11
    FlagAboveMaxCap     : BOOL;          // Bit 12
    FlagBelowMinCap     : BOOL;          // Bit 13
    FlagOKMinusAccepted : BOOL;          // Bit 14
    FlagNoUpstreamConsent: BOOL;         // Bit 15
    FlagInvalidPreweight: BOOL;          // Bit 16
    FlagOKAboveNominal  : BOOL;          // Bit 17
    FlagOKBelowNominal  : BOOL;          // Bit 18
    
    // Validità
    Valid               : BOOL;          // Dati validi
    ReceivedTime        : LINT;          // Timestamp ricezione
END_STRUCT;
END_TYPE
```

### 8.3 Struttura Dati: Idecon_BatchStats

```iecst
TYPE Idecon_BatchStats :
STRUCT
    // Header
    Timestamp           : STRING[32];
    BatchStartTime      : STRING[32];
    
    // Identificazione
    ProductionOrder     : STRING[64];
    ProductionCode      : STRING[64];
    RecipeName          : STRING[32];
    LineCode            : STRING[32];
    SerialNumber        : STRING[16];
    
    // Contatori Globali
    TotalProducts       : UDINT;
    TotalAccepted       : UDINT;
    RejectedMM          : UDINT;
    RejectedM           : UDINT;
    RejectedP           : UDINT;
    RejectedPP          : UDINT;
    CannotBeWeighed     : UDINT;
    MetalDetected       : UDINT;
    
    // Pesi (g)
    AverageWeight_g     : REAL;
    MinWeight_g         : REAL;
    MaxWeight_g         : REAL;
    TotalWeight_kg      : REAL;
    StdDeviation_g      : REAL;
    
    // Contatori Incrementali
    IncrProducts        : UDINT;
    IncrAccepted        : UDINT;
    IncrRejectedMM      : UDINT;
    IncrRejectedM       : UDINT;
    IncrRejectedP       : UDINT;
    IncrRejectedPP      : UDINT;
    
    // KPI
    YieldPercentage     : REAL;
    RejectionRate       : REAL;
    ProductionRate_PPM  : REAL;
    
    // Stato
    BatchActive         : BOOL;
    DataValid           : BOOL;
    
    // Campi extra
    ExtraField1         : STRING[64];
    ExtraField2         : STRING[64];
END_STRUCT;
END_TYPE
```

### 8.4 Esempio: Programma Principale

```iecst
PROGRAM Management_Checkweigher_Idecon
VAR
    // Istanze FB
    fbClient        : FB_IDECON_Client;
    fbParseWeight   : FB_ParseWeightMessage;
    fbParseStatP    : FB_ParseStatPMessage;
    fbParseEvent    : FB_ParseEventMessage;
    
    // Stato
    State           : INT := 0;
    LastCommandTime : LINT;
    PollInterval    : TIME := T#5S;
    
    // Buffer ricezione
    RxBuffer        : ARRAY[0..1023] OF BYTE;
    RxLen           : UINT;
    
    // Comandi
    CmdQueue        : ARRAY[0..9] OF STRING[255];
    CmdQueueHead    : INT := 0;
    CmdQueueTail    : INT := 0;
    
    // Dati
    CurrentWeight   : Idecon_WeightData;
    BatchStats      : Idecon_BatchStats;
    LastEvent       : Idecon_EventData;
END_VAR

// State Machine principale
CASE State OF
    0: // Connessione
        IF G_Idecon_Config.Connect THEN
            State := 10;
        END_IF;
        
    10: // Idle - Attesa comandi
        // Polling ciclico STATSV
        IF (CurrentTimestamp - LastCommandTime) > PollInterval THEN
            AddToQueue("STATSV");
            LastCommandTime := CurrentTimestamp;
        END_IF;
        
        // Processa coda comandi
        IF CmdQueueHead <> CmdQueueTail THEN
            fbClient.Command := CmdQueue[CmdQueueHead];
            fbClient.Execute := TRUE;
            State := 20;
        END_IF;
        
        // Check dati in arrivo
        IF Socket.Available > 0 THEN
            State := 30;
        END_IF;
        
    20: // Invio comando
        fbClient();
        IF fbClient.Done THEN
            ProcessResponse(fbClient.Response);
            fbClient.Execute := FALSE;
            CmdQueueHead := (CmdQueueHead + 1) MOD 10;
            State := 10;
        ELSIF fbClient.Error THEN
            HandleError(fbClient.ErrorID);
            fbClient.Execute := FALSE;
            State := 10;
        END_IF;
        
    30: // Ricezione dati asincroni
        Socket.Recv(RxBuffer, RxLen);
        ParseMessage(RxBuffer, RxLen);
        State := 10;
        
END_CASE;

// Gestione WEIGHT ricevuti
IF CurrentWeight.Valid AND CurrentWeight.ReceivedTime <> LastWeightTime THEN
    UpdateStatistics(CurrentWeight);
    SendToSCADA(CurrentWeight);
    LastWeightTime := CurrentWeight.ReceivedTime;
END_IF;
```

---

## 9. Checklist Implementazione

### Fase 1: Setup Iniziale
- [ ] Configurare IP/Porta bilancia in G_Idecon_Config
- [ ] Creare DataTypes (Idecon_WeightData, Idecon_BatchStats, ecc.)
- [ ] Aggiungere Global Variables per stato e statistiche
- [ ] Implementare FB_IDECON_Client
- [ ] Test connessione base (STATSV)

### Fase 2: Parsing Dati
- [ ] Implementare FB_ParseWeightMessage (19 bit classification)
- [ ] Implementare FB_ParseStatPMessage (50 campi)
- [ ] Implementare FB_ParseEventMessage
- [ ] Test parsing con dati reali

### Fase 3: Gestione Batch
- [ ] Implementare BATCHMODIFY per tutti i campi
- [ ] Implementare BATCHSTART/BATCHSTOP
- [ ] Verifica stato batch con STATSV
- [ ] Test ciclo completo batch

### Fase 4: Statistiche
- [ ] Implementare ENABLESTATS/DISABLESTATS
- [ ] Configurare STATCADENCY (30s)
- [ ] Test ricezione STATP automatici
- [ ] Calcolo KPI (Yield, Rejection Rate)

### Fase 5: Integrazione SCADA
- [ ] Mappare RecipeIndex → RecipeName
- [ ] Collegare S60_RecipeManagement a IDECON
- [ ] Collegare S62_UpdateProductionInfo a BATCHMODIFY
- [ ] Gestire flag CambioRicetta_Event e CambioLotto_Event

### Fase 6: Error Handling
- [ ] Implementare gestione timeout
- [ ] Gestire Error 30 (Negative Mean Error)
- [ ] Implementare G_System_Error
- [ ] Aggiungere diagnostica e logging

### Fase 7: Modalità REMOTE (Opzionale)
- [ ] Aggiungere verifica STATSV pos 7
- [ ] Implementare comando START/STOP (solo REMOTE)
- [ ] Aggiungere sicurezze (verifica REMOTE mode)
- [ ] Test produzione automatica

### Fase 8: Test e Validazione
- [ ] Test tutti i comandi con bilancia reale
- [ ] Verificare parsing corretto pesi
- [ ] Testare sequenze complete
- [ ] Validare integrazione SCADA
- [ ] Documentare anomalie e workaround

---

## 10. Note e Limitazioni

### 10.1 Limitazioni Conosciute

1. **Modalità REMOTE:** Richiede intervento operatore su HMI bilancia. Il PLC non può forzare il cambio da LOCAL a REMOTE.

2. **Cambio Ricetta:** Il comando RECIPE funziona solo con macchina ferma (STOPPED) e in REMOTE mode. In LOCAL mode, l'operatore deve cambiare manualmente.

3. **Batch Aperto:** Non è possibile modificare i campi batch (BATCHMODIFY) se il batch è già aperto. Bisogna chiudere (BATCHSTOP) e riaprire (BATCHSTART).

4. **Visualizzazione Messaggi:** SHOWMESSAGE funziona solo su bilance con HMI 12". Le versioni 7" non supportano questo comando.

5. **Lista Ricette:** GETRECIPELIST restituisce i nomi ma richiede parsing sequenziale dei messaggi DSxx.

### 10.2 Workaround

**Problema:** Bilancia in LOCAL, serve cambiare ricetta
**Soluzione:** 
1. PLC invia SHOWMESSAGE="Cambiare ricetta a [nome]"
2. Operatore cambia manualmente da HMI
3. PLC verifica con INFORECIPE

**Problema:** Errore 30 persistente
**Soluzione:**
1. Chiudi batch (BATCHSTOP)
2. Apri nuovo batch (BATCHSTART) → statistiche azzerate
3. Continua produzione

**Problema:** Timeout frequenti
**Soluzione:**
1. Aumentare timeout a 10s
2. Verificare carico rete
3. Ridurre frequenza STATSV polling (da 5s a 10s)

---

## 11. Riferimenti

- Manuale Protocollo: `06_Manuals/WeigherTCP IDECON v2.7_EN.md`
- Manuale OPC-UA: `06_Manuals/Communication protocol for IDECON weigher - OPC-UA v1.3_EN.pdf`
- Manuale WP: `06_Manuals/Manual WP (M) rev. 123.00.05 - EN.pdf`
- Test Python: `test_*.py` files (validati)

---

**Autore:** Claude  
**Ultima Modifica:** 2026-02-10  
**Stato:** Pronto per Implementazione PLC