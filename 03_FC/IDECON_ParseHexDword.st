// ==============================================================================
// FUNZIONE: IDECON_ParseHexDword
// DESCRIZIONE: Converte una stringa esadecimale (es. '0x80') in DWORD
// ==============================================================================

// Variabili Interne:
// i, n : UINT
// sCh : STRING[1]
// posUpper, posLower : INT
// v, d : DINT
v := 0;
n := LEN(InText);
i := 1;

// Skip '0x'
IF n >= 2 THEN
    IF (MID(InText, 2, 1) = '0x') OR (MID(InText, 2, 1) = '0X') THEN i := 3; END_IF;
END_IF;

WHILE i <= n DO
    // Estrai carattere corrente
    // Usiamo FIND su stringhe letterali che è supportato ovunque
    // Cerchiamo il carattere nella mappa Hex
    
    // Cerca in "0123456789ABCDEFabcdef"
    // Posizione: 1=0, 10=9, 11=A, 16=F, 17=a, 22=f
    
    // Nota: MID(Source, Len, Pos)
    // FIND(Source, Target) -> Ritorna 1-based index
    
    d := 0; // Reset valore cifra
    
    // Cerca 0-9
    posUpper := FIND('0123456789', MID(InText, 1, i));
    IF posUpper > 0 THEN
        d := INT_TO_DINT(posUpper - 1); // '0'->1->0, '9'->10->9
        v := (v * 16) + d;
    ELSE
        // Cerca A-F
        posUpper := FIND('ABCDEF', MID(InText, 1, i));
        IF posUpper > 0 THEN
            d := INT_TO_DINT(posUpper - 1) + 10; // 'A'->1->10
            v := (v * 16) + d;
        ELSE
            // Cerca a-f
            posLower := FIND('abcdef', MID(InText, 1, i));
            IF posLower > 0 THEN
                d := INT_TO_DINT(posLower - 1) + 10; // 'a'->1->10
                v := (v * 16) + d;
            END_IF;
        END_IF;
    END_IF;
    
    i := i + 1;
END_WHILE;

IDECON_ParseHexDword := DINT_TO_DWORD(v);
