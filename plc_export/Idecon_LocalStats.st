// ============================================================================
// DataType: Idecon_LocalStats
// Description: Statistiche locali calcolate dal PLC (indipendenti da bilancia)
// ============================================================================

TYPE Idecon_LocalStats :
STRUCT
    // === Contatori Totali ====================================================
    TotalWeights            : UDINT;            // Totale pesi ricevuti
    TotalAccepted           : UDINT;            // Totale OK
    TotalRejected           : UDINT;            // Totale scartati
    TotalExpelled           : UDINT;            // Totale espulsi
    
    // === Contatori per Categoria =============================================
    CountOK                 : UDINT;            // Solo OK
    CountOKPlus             : UDINT;            // OK+
    CountOKMinus            : UDINT;            // OK-
    CountPlus               : UDINT;            // +
    CountPlusPlus           : UDINT;            // ++
    CountMinus              : UDINT;            // -
    CountMinusMinus         : UDINT;            // --
    CountMetal              : UDINT;            // Con metallo
    
    // === Pesi (calcolati in g) ===============================================
    SumWeight_g             : REAL;             // Somma pesi (per media)
    AvgWeight_g             : REAL;             // Media pesi
    MinWeight_g             : REAL;             // Peso minimo rilevato
    MaxWeight_g             : REAL;             // Peso massimo rilevato
    
    // === Timing ==============================================================
    FirstWeightTime         : LINT;             // Timestamp prima pesata
    LastWeightTime          : LINT;            // Timestamp ultima pesata
    ProductionTime_sec      : UDINT;            // Tempo produzione (secondi)
    
    // === Allarmi =============================================================
    Error30_Count           : UDINT;            // Quanti errori 30 ricevuti
    OtherErrors_Count       : UDINT;            // Altri errori
    
    // === Reset ===============================================================
    Reset                   : BOOL;             // Azzera contatori
    
END_STRUCT;
END_TYPE