# IdeconInterface - Struttura Unificata

## Overview

Invece di avere decine di variabili sparse in Global Variables, usiamo **UNA SOLA** struttura principale:

```iecst
G_Idecon : IdeconInterface;
```

## Gerarchia delle Strutture

```
IdeconInterface (STRUCT principale)
│
├── Config (Idecon_Config)
│   ├── IpAddress : STRING[15]
│   ├── TcpPort : UINT
│   ├── ConnectionTimeout_ms : UDINT
│   ├── CommandTimeout_ms : UDINT
│   ├── PollInterval_ms : UDINT
│   ├── MaxRetries : UINT
│   ├── MsgFilterValue : UINT
│   ├── StatsCadency_sec : UINT
│   ├── Connect : BOOL
│   └── AutoReconnect : BOOL
│
├── Socket (_sSOCKET - built-in)
│
├── Comm (Idecon_CommStatus)
│   ├── Connected : BOOL
│   ├── Online : BOOL
│   ├── Ready : BOOL
│   ├── RxCount : UDINT
│   ├── TxCount : UDINT
│   ├── ErrorCount : UDINT
│   ├── LastRxTime : LINT
│   ├── StatusCode : STRING[8]
│   ├── WorkMode : UINT
│   ├── IsLocalMode : BOOL
│   └── IsRemoteMode : BOOL
│
├── LastWeight (Idecon_WeightData)
│   ├── Timestamp : STRING[32]
│   ├── ProductionOrder : STRING[64]
│   ├── BatchCode : STRING[64]
│   ├── RecipeName : STRING[32]
│   ├── WeightMg : DINT
│   ├── DeltaMg : DINT
│   ├── Classification : UDINT
│   ├── FlagWeightOK : BOOL
│   ├── FlagExpelled : BOOL
│   └── ... (19 flag totali)
│
├── BatchStats (Idecon_BatchStats)
│   ├── TotalProducts : UDINT
│   ├── TotalAccepted : UDINT
│   ├── AverageWeight_g : REAL
│   ├── YieldPercentage : REAL
│   └── ... (50+ campi)
│
├── Status (Idecon_Status)
│   ├── StatusCode : STRING[8]
│   ├── MotorRunning : BOOL
│   ├── ProductionStarted : BOOL
│   ├── HasErrors : BOOL
│   ├── WorkMode : UINT
│   └── ...
│
├── LastEvent (Idecon_EventData)
│   ├── EventCode : UINT
│   ├── EventDescription : STRING[255]
│   └── ...
│
├── Cmd (Idecon_Command)
│   ├── Execute : BOOL
│   ├── Command : STRING[255]
│   ├── Done : BOOL
│   ├── Busy : BOOL
│   ├── Error : BOOL
│   └── Response : STRING[512]
│
├── Stats (Idecon_LocalStats)
│   ├── TotalWeights : UDINT
│   ├── AvgWeight_g : REAL
│   └── ...
│
└── SystemError : BOOL
```

## Configurazione in HSM_SpecificationsSetting

Aggiungere alla fine del file, dopo la configurazione assi:

```iecst
//====================== IDECON WEIGHER - SETTING =========================
IF P_First_RunMode THEN
    
    // Configurazione bilancia IDECON (stile AXIS[..])
    G_Idecon.Config.IpAddress := '172.16.224.210';
    G_Idecon.Config.TcpPort := 50000;
    G_Idecon.Config.ConnectionTimeout_ms := 10000;
    G_Idecon.Config.CommandTimeout_ms := 5000;
    G_Idecon.Config.PollInterval_ms := 5000;
    G_Idecon.Config.MaxRetries := 3;
    G_Idecon.Config.MsgFilterValue := 23;  // Errori + Eventi + Pesi
    G_Idecon.Config.StatsCadency_sec := 30;
    G_Idecon.Config.AutoReconnect := TRUE;
    G_Idecon.Config.Connect := FALSE;  // Abilitato dopo da programma
    
END_IF;
```

## Uso nei Function Block

### Prima (variabili singole):
```iecst
// Global Variables
G_Idecon_Socket : _sSOCKET;
G_Idecon_Command : STRING[255];
G_Idecon_Execute : BOOL;
G_Idecon_Done : BOOL;
G_Idecon_Response : STRING[512];
G_Idecon_LastWeight : Idecon_WeightData;

// Nel programma
fbClient(
    Socket := G_Idecon_Socket,
    Command := G_Idecon_Command,
    Execute := G_Idecon_Execute,
    Done => G_Idecon_Done,
    Response => G_Idecon_Response
);

IF G_Idecon_LastWeight.Valid THEN
    // usa G_Idecon_LastWeight.WeightMg
END_IF;
```

### Dopo (struttura unificata):
```iecst
// Global Variables - UNA SOLA RIGA!
G_Idecon : IdeconInterface;

// Nel programma
fbClient(
    Socket := G_Idecon.Socket,
    Command := G_Idecon.Cmd.Command,
    Execute := G_Idecon.Cmd.Execute,
    Done => G_Idecon.Cmd.Done,
    Response => G_Idecon.Cmd.Response
);

IF G_Idecon.LastWeight.Valid THEN
    // usa G_Idecon.LastWeight.WeightMg
END_IF;
```

## Accesso ai Dati - Esempi Pratici

### Verifica stato connessione:
```iecst
IF G_Idecon.Comm.Connected AND G_Idecon.Comm.Online THEN
    // Comunicazione OK
END_IF;
```

### Controllo modalità (LOCAL vs REMOTE):
```iecst
IF G_Idecon.Comm.IsRemoteMode THEN
    // Posso inviare START
    G_Idecon.Cmd.Command := 'START';
    G_Idecon.Cmd.Execute := TRUE;
ELSE
    // Solo BATCHSTART/BATCHSTOP
END_IF;
```

### Lettura ultimo peso:
```iecst
IF G_Idecon.LastWeight.Valid THEN
    Weight_g := DINT_TO_REAL(G_Idecon.LastWeight.WeightMg) / 1000.0;
    
    IF G_Idecon.LastWeight.FlagExpelled THEN
        // Prodotto scartato
    ELSIF G_Idecon.LastWeight.FlagWeightOK THEN
        // Prodotto OK
    END_IF;
END_IF;
```

### Invio comando:
```iecst
// Prepara comando
G_Idecon.Cmd.Command := 'BATCHMODIFY=PRODUCTIONORDER|ORD2024001';
G_Idecon.Cmd.Timeout := T#5S;

// Esegui
G_Idecon.Cmd.Execute := TRUE;

// Attendi completamento
IF G_Idecon.Cmd.Done THEN
    // Comando OK
    G_Idecon.Cmd.Execute := FALSE;
ELSIF G_Idecon.Cmd.Error THEN
    // Gestione errore
    ErrorCode := G_Idecon.Cmd.ErrorID;
    G_Idecon.Cmd.Execute := FALSE;
END_IF;
```

### Statistiche batch:
```iecst
IF G_Idecon.BatchStats.DataValid THEN
    TotalPieces := G_Idecon.BatchStats.TotalProducts;
    Yield := G_Idecon.BatchStats.YieldPercentage;
    AvgWeight := G_Idecon.BatchStats.AverageWeight_g;
END_IF;
```

### Contatori locali PLC:
```iecst
// G_Idecon.Stats si aggiorna automaticamente ad ogni pesata
TotalReceived := G_Idecon.Stats.TotalWeights;
LocalAverage := G_Idecon.Stats.AvgWeight_g;

// Reset quando serve
IF ResetCounters THEN
    G_Idecon.Stats.Reset := TRUE;
ELSE
    G_Idecon.Stats.Reset := FALSE;
END_IF;
```

## Vantaggi

✅ **Una sola variabile** in Global Variables  
✅ **Organizzazione gerarchica** chiara e logica  
✅ **Passaggio semplice** ai FB (solo G_Idecon)  
✅ **Debugging facilitato** - tutto raggruppato  
✅ **Consistente** con stile AXIS e ScadaInterface  
✅ **Espandibile** - aggiungere campi in una struct non rompe il codice esistente

## File da Importare

Ordine di importazione in Sysmac Studio:

1. **Idecon_Config.st** - Configurazione
2. **Idecon_CommStatus.st** - Stato comunicazione
3. **Idecon_Command.st** - Gestione comandi
4. **Idecon_LocalStats.st** - Statistiche locali
5. **Idecon_Types.st** - Tipi di base (Status, EventData)
6. **Idecon_WeightData.st** - Dati peso
7. **Idecon_BatchStats.st** - Statistiche batch
8. **IdeconInterface.st** - Struttura principale (dipende da tutte le precedenti)

## Integrazione con Codice Esistente

### Collegamento a S60_RecipeManagement:
```iecst
// In S60, quando cambia ricetta:
IF RecipeChange_State = ProcessingAccepted THEN
    // Mappa RecipeIndex → RecipeName bilancia
    CASE L_InRecipeIndex OF
        1: TargetRecipe := '225g';
        2: TargetRecipe := '450g';
        3: TargetRecipe := '900g';
    END_CASE;
    
    // Se in REMOTE mode, invia comando
    IF G_Idecon.Comm.IsRemoteMode THEN
        G_Idecon.Cmd.Command := CONCAT('RECIPE=', TargetRecipe);
        G_Idecon.Cmd.Execute := TRUE;
    END_IF;
END_IF;
```

### Collegamento a S62_UpdateProductionInfo:
```iecst
// In S62, quando aggiorna produzione:
IF ProductionChange_State = ProcessingAccepted THEN
    // Invia campi a bilancia
    G_Idecon.Cmd.Command := CONCAT('BATCHMODIFY=PRODUCTIONORDER|', 
                                   ScadaInterface.Egress.ActualProductionInfo);
    G_Idecon.Cmd.Execute := TRUE;
END_IF;
```

## Troubleshooting

### "Type not defined"
**Causa:** Importazione non nell'ordine corretto  
**Soluzione:** Importare prima le struct dipendenti (Config, CommStatus, ecc.), poi IdeconInterface alla fine

### "Circular reference"
**Causa:** IdeconInterface importato prima delle sotto-struct  
**Soluzione:** Seguire l'ordine di importazione specificato sopra

### Campi non visibili in watch window
**Causa:** Struct troppo grande per watch inline  
**Soluzione:** Espandere G_Idecon e navigare nei sotto-livelli, oppure usare G_Idecon.LastWeight.WeightMg direttamente