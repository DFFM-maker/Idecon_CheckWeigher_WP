// ============================================================================
// Function: IDECON_StartsWith
// Description: Verifica se una stringa inizia con un prefisso
// ============================================================================

FUNCTION IDECON_StartsWith : BOOL
VAR_INPUT
    Str                     : STRING[512];      // Stringa da verificare
    Prefix                  : STRING[64];       // Prefisso da cercare
END_VAR

VAR
    StrLen                  : UINT;
    PrefixLen               : UINT;
END_VAR;

StrLen := LEN(Str);
PrefixLen := LEN(Prefix);

IF PrefixLen = 0 THEN
    IDECON_StartsWith := TRUE;
    RETURN;
END_IF;

IF StrLen < PrefixLen THEN
    IDECON_StartsWith := FALSE;
    RETURN;
END_IF;

IDECON_StartsWith := (LEFT(Str, PrefixLen) = Prefix);

END_FUNCTION

// ============================================================================
// Function: IDECON_FieldAt
// Description: Estrae campo N da stringa delimitata
// ============================================================================

FUNCTION IDECON_FieldAt : STRING[64]
VAR_INPUT
    Str                     : STRING[512];      // Stringa sorgente
    FieldNum                : UINT;             // Numero campo (1-based)
    Delimiter               : STRING[1];        // Delimitatore
END_VAR

VAR
    i                       : INT;
    CurrentField            : UINT;
    StartPos                : INT;
    StrLen                  : UINT;
END_VAR;

StrLen := LEN(Str);
IF StrLen = 0 OR FieldNum = 0 THEN
    IDECON_FieldAt := '';
    RETURN;
END_IF;

CurrentField := 1;
StartPos := 1;

FOR i := 1 TO INT#(StrLen) DO
    IF MID(Str, 1, UINT#(i)) = Delimiter THEN
        IF CurrentField = FieldNum THEN
            // Campo trovato
            IDECON_FieldAt := MID(Str, UINT#(i - StartPos), UINT#(StartPos));
            RETURN;
        END_IF;
        CurrentField := CurrentField + 1;
        StartPos := i + 1;
    END_IF;
END_FOR;

// Ultimo campo
IF CurrentField = FieldNum THEN
    IDECON_FieldAt := MID(Str, UINT#(StrLen - StartPos + 1), UINT#(StartPos));
ELSE
    IDECON_FieldAt := '';
END_IF;

END_FUNCTION

// ============================================================================
// Function: IDECON_ParseHexDword
// Description: Converte stringa esadecimale in UDINT
// ============================================================================

FUNCTION IDECON_ParseHexDword : UDINT
VAR_INPUT
    HexStr                  : STRING[16];       // Stringa hex (es. "20480")
END_VAR

VAR
    Result                  : UDINT;
    i                       : INT;
    StrLen                  : UINT;
    Digit                   : BYTE;
    CharVal                 : UDINT;
END_VAR;

StrLen := LEN(HexStr);
Result := UDINT#0;

FOR i := 1 TO INT#(StrLen) DO
    Digit := STRING_TO_BYTE(MID(HexStr, 1, UINT#(i)));
    
    IF Digit >= BYTE#48 AND Digit <= BYTE#57 THEN
        // '0'-'9'
        CharVal := BYTE_TO_UDINT(Digit) - UDINT#48;
    ELSIF Digit >= BYTE#65 AND Digit <= BYTE#70 THEN
        // 'A'-'F'
        CharVal := BYTE_TO_UDINT(Digit) - UDINT#55;
    ELSIF Digit >= BYTE#97 AND Digit <= BYTE#102 THEN
        // 'a'-'f'
        CharVal := BYTE_TO_UDINT(Digit) - UDINT#87;
    ELSE
        CONTINUE; // Carattere non valido, salta
    END_IF;
    
    Result := Result * UDINT#16 + CharVal;
END_FOR;

IDECON_ParseHexDword := Result;

END_FUNCTION