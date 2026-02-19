// ============================================================================
// DataType: Idecon_BatchStats
// Description: Statistiche batch da messaggio STATP (50 campi)
// Version: 1.0
// ============================================================================

TYPE Idecon_BatchStats :
STRUCT
    // === Header (Campi 1-7) ==================================================
    Timestamp               : STRING[32];       // Data/ora statistiche
    BatchStartTime          : STRING[32];       // Inizio batch
    ProductionOrder         : STRING[64];       // Ordine produzione
    ProductionCode          : STRING[64];       // Codice prodotto
    RecipeName              : STRING[32];       // Nome ricetta
    LineCode                : STRING[32];       // Codice linea
    SerialNumber            : STRING[16];       // Serial number
    
    // === Contatori Global Batch (Campi 8-22) =================================
    TotalProducts           : UDINT;            // Totale pezzi (Campo 8)
    TotalAccepted           : UDINT;            // Totale accettati (Campo 9)
    RejectedMinusMinus      : UDINT;            // Scartati -- (Campo 13)
    RejectedMinus           : UDINT;            // Scartati - (Campo 14)
    RejectedPlus            : UDINT;            // Scartati + (Campo 15)
    RejectedPlusPlus        : UDINT;            // Scartati ++ (Campo 16)
    CannotBeWeighed         : UDINT;            // Non pesabili (Campo 17)
    MetalDetected           : UDINT;            // Metallo rilevato (Campo 18)
    
    // === Metal Test (Campi 19-22) ============================================
    MetalTestsPerformed     : UDINT;            // Test metallo eseguiti
    MetalTestsPassed        : UDINT;            // Test superati
    MetalTestsFailed        : UDINT;            // Test falliti
    MetalTestsRefused       : UDINT;            // Test rifiutati
    
    // === Pesi Campione OK (Campi 10-12, 23-26) ===============================
    AverageWeight_g         : REAL;             // Peso medio accettati (g)
    MinWeight_g             : REAL;             // Peso minimo accettati (g)
    MaxWeight_g             : REAL;             // Peso massimo accettati (g)
    
    // Ultimo peso (Campi 23-26)
    LastWeightExact_g       : REAL;             // Ultimo peso esatto (g)
    LastWeightRounded_g     : REAL;             // Ultimo peso arrotondato (g)
    LastWeightDiff_g        : REAL;             // Ultimo delta (g)
    LastWeightClass         : STRING[16];       // Classe ultimo peso
    
    // === Contatori Incrementali (Campi 27-46) ================================
    IncrProducts            : UDINT;            // Incrementale totale
    IncrAccepted            : UDINT;            // Incrementale accettati
    IncrRejectedMM          : UDINT;            // Incrementale --
    IncrRejectedM           : UDINT;            // Incrementale -
    IncrRejectedP           : UDINT;            // Incrementale +
    IncrRejectedPP          : UDINT;            // Incrementale ++
    IncrCannotBeWeighed     : UDINT;            // Incrementale non pesabili
    IncrMetalDetected       : UDINT;            // Incrementale metallo
    
    // === KPI (Campi 47-50) ===================================================
    OKMinusProducts         : UDINT;            // OK- prodotti (Campo 48)
    OKMinusAccepted         : UDINT;            // OK- accettati (Campo 49)
    StandardDeviation_g     : REAL;             // Deviazione standard (Campo 50)
    
    // === KPI Calcolati =======================================================
    YieldPercentage         : REAL;             // Rendimento % (Accepted/Total*100)
    RejectionRate           : REAL;             // Tasso scarto %
    ProductionRate_PPM      : REAL;             // Pezzi al minuto
    TotalWeight_kg          : REAL;             // Peso totale kg
    
    // === Stato e Validità ====================================================
    BatchActive             : BOOL;             // Batch attivo
    DataValid               : BOOL;             // Dati validi
    ReceivedTime            : LINT;             // Timestamp ricezione
    LastUpdateTime          : LINT;             // Ultimo aggiornamento
    ParseError              : BOOL;             // Errore parsing
    ErrorCode               : UINT;             // Codice errore
    
    // === Campi Extra dal Batch ===============================================
    ExtraField1             : STRING[64];       // Campo extra 1
    ExtraField2             : STRING[64];       // Campo extra 2
    UserName                : STRING[32];       // Nome operatore
    
END_STRUCT;
END_TYPE