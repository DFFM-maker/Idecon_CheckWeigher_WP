// ============================================================================
// Function Block: FB_ParseWeightMessage
// Description: Parsa messaggio WEIGHT dalla bilancia IDECON
// Version: 1.0
// ============================================================================

FUNCTION_BLOCK FB_ParseWeightMessage
VAR_INPUT
    Enable                  : BOOL;             // Abilita parsing
    Message                 : STRING[512];      // Messaggio da parsare
    MessageRaw              : ARRAY[0..511] OF BYTE;
    MessageLen              : UINT;
END_VAR

VAR_OUTPUT
    Done                    : BOOL;             // Parsing completato
    Error                   : BOOL;             // Errore parsing
    ErrorCode               : UINT;             // Codice errore
    WeightData              : Idecon_WeightData; // Dati peso parsati
END_VAR

VAR
    // Variabili interne
    MsgTemp                 : STRING[512];
    Parts                   : ARRAY[0..10] OF STRING[64];
    NumParts                : INT;
    i                       : INT;
    Pos                     : INT;
    LastPos                 : INT;
    ClassificationValue     : UDINT;
    
END_VAR

// ============================================================================
// IMPLEMENTAZIONE
// ============================================================================

IF NOT Enable THEN
    Done := FALSE;
    Error := FALSE;
    ErrorCode := UINT#0;
    RETURN;
END_IF;

// Verifica prefisso WEIGHT=
IF NOT IDECON_StartsWith(Message, 'WEIGHT=') THEN
    Error := TRUE;
    ErrorCode := UINT#1; // Prefisso non valido
    RETURN;
END_IF;

// Rimuovi prefisso
MsgTemp := DELETE(Message, 7, 1); // Rimuovi "WEIGHT="

// Split per |
NumParts := 0;
Pos := 1;
LastPos := 1;

FOR i := 1 TO LEN(MsgTemp) DO
    IF MID(MsgTemp, 1, UINT#(i)) = '|' THEN
        IF NumParts <= 9 THEN
            Parts[NumParts] := MID(MsgTemp, UINT#(i - LastPos), UINT#(LastPos));
            NumParts := NumParts + 1;
            LastPos := i + 1;
        END_IF;
    END_IF;
END_FOR;

// Ultimo campo
IF NumParts <= 9 AND LastPos <= LEN(MsgTemp) THEN
    Parts[NumParts] := MID(MsgTemp, UINT#(LEN(MsgTemp) - LastPos + 1), UINT#(LastPos));
    NumParts := NumParts + 1;
END_IF;

// Verifica numero campi
IF NumParts < 9 THEN
    Error := TRUE;
    ErrorCode := UINT#2; // Numero campi insufficiente
    WeightData.ParseError := TRUE;
    WeightData.ErrorCode := UINT#2;
    RETURN;
END_IF;

// Parsing campi
WeightData.Timestamp := Parts[0];
WeightData.ProductionOrder := Parts[1];
WeightData.BatchCode := Parts[2];
WeightData.RecipeName := Parts[3];
WeightData.LineCode := Parts[4];
WeightData.SerialNumber := Parts[5];

// Conversione numerica
WeightData.WeightMg := STRING_TO_DINT(Parts[6]);
WeightData.DeltaMg := STRING_TO_DINT(Parts[7]);

// Parsing classification (hex)
ClassificationValue := STRING_TO_UDINT(Parts[8]);
WeightData.Classification := ClassificationValue;

// Decodifica bit
WeightData.FlagProductTooLong := (ClassificationValue AND UDINT#16#000001) > UDINT#0;
WeightData.FlagProductTooShort := (ClassificationValue AND UDINT#16#000002) > UDINT#0;
WeightData.FlagMetal := (ClassificationValue AND UDINT#16#000004) > UDINT#0;
WeightData.FlagWeightPlusPlus := (ClassificationValue AND UDINT#16#000008) > UDINT#0;
WeightData.FlagWeightPlus := (ClassificationValue AND UDINT#16#000010) > UDINT#0;
WeightData.FlagWeightMinusMinus := (ClassificationValue AND UDINT#16#000020) > UDINT#0;
WeightData.FlagWeightMinus := (ClassificationValue AND UDINT#16#000040) > UDINT#0;
WeightData.FlagWeightOK := (ClassificationValue AND UDINT#16#000080) > UDINT#0;
WeightData.FlagExpelled := (ClassificationValue AND UDINT#16#000100) > UDINT#0;
WeightData.FlagProductTooClose := (ClassificationValue AND UDINT#16#000200) > UDINT#0;
WeightData.FlagNewDynamicTare := (ClassificationValue AND UDINT#16#000400) > UDINT#0;
WeightData.FlagIncorrectTare := (ClassificationValue AND UDINT#16#000800) > UDINT#0;
WeightData.FlagAboveMaxCapacity := (ClassificationValue AND UDINT#16#001000) > UDINT#0;
WeightData.FlagBelowMinCapacity := (ClassificationValue AND UDINT#16#002000) > UDINT#0;
WeightData.FlagOKMinusAccepted := (ClassificationValue AND UDINT#16#004000) > UDINT#0;
WeightData.FlagNoUpstreamConsent := (ClassificationValue AND UDINT#16#008000) > UDINT#0;
WeightData.FlagInvalidPreweight := (ClassificationValue AND UDINT#16#010000) > UDINT#0;
WeightData.FlagOKAboveNominal := (ClassificationValue AND UDINT#16#020000) > UDINT#0;
WeightData.FlagOKBelowNominal := (ClassificationValue AND UDINT#16#040000) > UDINT#0;

// Validazione
WeightData.Valid := TRUE;
WeightData.ParseError := FALSE;
WeightData.ErrorCode := UINT#0;
WeightData.ReceivedTime := 0; // Da impostare chiamante

Done := TRUE;
Error := FALSE;

END_FUNCTION_BLOCK