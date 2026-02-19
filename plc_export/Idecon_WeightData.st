// ============================================================================
// DataType: Idecon_WeightData
// Description: Struttura dati per messaggio WEIGHT dalla bilancia IDECON
// Version: 1.0
// ============================================================================

TYPE Idecon_WeightData :
STRUCT
    // === Identificazione =====================================================
    Timestamp               : STRING[32];       // Data/ora pesata (yyyy.mm.dd hh:mm:ss:msec)
    ProductionOrder         : STRING[64];       // Ordine produzione
    BatchCode               : STRING[64];       // Codice batch/lotto
    RecipeName              : STRING[32];       // Nome ricetta (es. "225g")
    LineCode                : STRING[32];       // Codice linea
    SerialNumber            : STRING[16];       // Serial number bilancia
    
    // === Valori numerici (in milligrammi) ====================================
    WeightMg                : DINT;             // Peso rilevato in mg
    DeltaMg                 : DINT;             // Delta da peso nominale in mg
    Classification          : UDINT;            // Bitmap classificazione (19 bit)
    
    // === Flag decodificati (19 bit di Classification) ========================
    // Bit 0-2: Caratteristiche fisiche
    FlagProductTooLong      : BOOL;             // Prodotto troppo lungo (Bit 0)
    FlagProductTooShort     : BOOL;             // Prodotto troppo corto (Bit 1)
    FlagMetal               : BOOL;             // Rilevato metallo (Bit 2)
    
    // Bit 3-7: Categorie peso
    FlagWeightPlusPlus      : BOOL;             // Categoria ++ (Bit 3)
    FlagWeightPlus          : BOOL;             // Categoria + (Bit 4)
    FlagWeightMinusMinus    : BOOL;             // Categoria -- (Bit 5)
    FlagWeightMinus         : BOOL;             // Categoria - (Bit 6)
    FlagWeightOK            : BOOL;             // Categoria OK (Bit 7)
    
    // Bit 8-11: Condizioni speciali
    FlagExpelled            : BOOL;             // Espulso (Bit 8)
    FlagProductTooClose     : BOOL;             // Prodotto troppo vicino (Bit 9)
    FlagNewDynamicTare      : BOOL;             // Nuova tara dinamica (Bit 10)
    FlagIncorrectTare       : BOOL;             // Tara incorretta (Bit 11)
    
    // Bit 12-13: Fuori range
    FlagAboveMaxCapacity    : BOOL;             // Sopra capacità max (Bit 12)
    FlagBelowMinCapacity    : BOOL;             // Sotto capacità min (Bit 13)
    
    // Bit 14-18: Condizioni OK speciali
    FlagOKMinusAccepted     : BOOL;             // OK- accettato (Bit 14)
    FlagNoUpstreamConsent   : BOOL;             // No consenso upstream (Bit 15)
    FlagInvalidPreweight    : BOOL;             // Peso pre-pesata invalido (Bit 16)
    FlagOKAboveNominal      : BOOL;             // OK sopra nominale (Bit 17)
    FlagOKBelowNominal      : BOOL;             // OK sotto nominale (Bit 18)
    
    // === Validità e timestamp ================================================
    Valid                   : BOOL;             // Dati validi (ricevuti e parsati)
    ReceivedTime            : LINT;             // Timestamp ricezione (Unix ms)
    ParseError              : BOOL;             // Errore parsing
    ErrorCode               : UINT;             // Codice errore parsing
    
END_STRUCT;
END_TYPE