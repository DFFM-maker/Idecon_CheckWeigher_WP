# FB_IDECON_Client — Release Notes

Piattaforma: Omron NJ501-1300 / Sysmac Studio
Protocollo: Idecon Checkweigher TCP (STX/ETX framing)

---

## v1.1 — Fix State 99 Random
**File:** `FB_IDECON_Client.st` + `Var_FB_IDECON_Client.st`
**Baseline:** `FB_IDECON_Client funzionante.st` (v1.0)

### Problema risolto
Il FB transitava a State 99 (errore/riconnessione) in modo casuale durante il
funzionamento normale, anche con connessione TCP stabile e dati ricevuti correttamente.

### Root Cause
**BUG #1 — Critico** (linea ~682):
`SktTCPRcv` con `TimeOut=0` (non-bloccante) può restituire `Error=TRUE` con
`ErrorID=0x2006` quando il receive buffer è vuoto ma la connessione è viva.
Questo è un comportamento benigno equivalente a `0x0400` (timeout), ma il controllo
di State 99 escludeva solo `0x0400`, non `0x2006`. Risultato: ogni scan senza dati
poteva triggerare una riconnessione non necessaria.

**BUG #2 — Secondario** (linea ~246):
La variabile `bNeedRcvRestart` non escludeva `0x2006`, portando a un mancato
riavvio rapido della ricezione in caso di errore benigno (risolto dal fallback,
ma con latenza extra e finestra temporale aperta per BUG#1).

### Fix applicati

#### 1. `bNeedRcvRestart` — esclusione 0x2006

```pascal
// v1.0 (con bug):
bNeedRcvRestart := NOT (bRcvError AND wRcvErrorID <> WORD#16#0400);

// v1.1 (corretto):
bNeedRcvRestart := NOT (bRcvError
                        AND wRcvErrorID <> WORD#16#0400
                        AND wRcvErrorID <> WORD#16#2006);
```

#### 2. Condizione State 99 — esclusione 0x2006

```pascal
// v1.0 (con bug):
IF bConnectError OR (bRcvError AND wRcvErrorID <> WORD#16#0400) THEN

// v1.1 (corretto):
IF bConnectError OR (bRcvError
                     AND wRcvErrorID <> WORD#16#0400
                     AND wRcvErrorID <> WORD#16#2006) THEN
```

#### 3. Diagnostica State 99 (nuova)

Aggiunto logging strutturato prima di ogni transizione a State 99:

| Variabile | Tipo | Descrizione |
|-----------|------|-------------|
| `Debug_State99Reason` | UINT | Motivo: 1=Watchdog, 2=RcvError, 3=ConnectError |
| `Debug_State99ErrorID` | WORD | ErrorID che ha causato la transizione |
| `Debug_State99Count` | UDINT | Contatore totale transizioni a State 99 |
| `Debug_WdogFireCount` | UDINT | Contatore scatti watchdog 60s |
| `Debug_RcvSoftErrCount` | UDINT | Contatore errori benigni 0x0400+0x2006 |

### Classificazione errori SktTCPRcv

| ErrorID | Significato | Azione corretta |
|---------|-------------|-----------------|
| `0x0400` | Timeout (TimeOut>0, nessun dato nel periodo) | Riavvia ricezione — NON State 99 |
| `0x2006` | Buffer vuoto (TimeOut=0, connessione viva) | Riavvia ricezione — NON State 99 |
| Altro | Errore reale (connessione chiusa/reset remoto) | State 99 → riconnessione |

### File versione precedente
`FB_IDECON_Client funzionante.st` — versione v1.0 pre-fix (baseline di riferimento)

---

## v1.0 — Versione funzionante con fix #1 #2 #3
**File:** `FB_IDECON_Client funzionante.st`

### Fix inclusi rispetto alla versione originale

| Fix | Descrizione |
|-----|-------------|
| #1 | `TimeOut=0` — nessun falso errore `0x0400` su ricezione non-bloccante |
| #2 | `bNeedRcvRestart` — gap ricezione ridotto a 1 scan dopo ogni Done/Error |
| #3 | State 99 — reset completo FB ricezione + flush buffer + reset CmdSent |

### Funzionalità
- Connessione/riconnessione automatica TCP
- Invio MSGFILTER=23 a connessione stabilita
- Buffer accumulo con parsing STX/ETX
- Dispatcher: WEIGHT / EVENT / STATSV / STATP / MSGFILTER / NEWPIECE
- Parser HEX per campo Classification (bitmap 19 bit)
- Statistiche Welford online (media, stddev, min/max, contatori per classe)
- Watchdog RX 60s con riconnessione automatica

---

## Suggerimenti per monitoring in produzione

```pascal
// Nel programma di supervisione, monitorare:

// Riconnessioni spurie risolte:
IF fbIdecon.Debug_State99Count > 0 THEN
    // Loggare: Reason, ErrorID, Count
END_IF;

// Soft errors (benigni, informativi):
// Debug_RcvSoftErrCount alto = normale in produzione (molti scan senza dati)

// Watchdog fires (possibile se Idecon silenziosa > 60s):
// Debug_WdogFireCount > 0 = verificare se Idecon invia STATSV regolarmente

// Errori reali di connessione:
// Debug_State99Reason = 2 (RcvError reale) o 3 (ConnectError)
// → verificare rete/dispositivo Idecon
```
