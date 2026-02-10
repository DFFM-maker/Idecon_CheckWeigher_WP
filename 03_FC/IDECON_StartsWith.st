// ==============================================================================
// FUNZIONE: IDECON_StartsWith
// DESCRIZIONE: Restituisce TRUE se InText inizia con Prefix
// ==============================================================================

// Variabili Interne:
// prefixLenU : UINT
// prefixLen, textLen : INT

prefixLenU := LEN(Prefix);
prefixLen := UINT_TO_INT(prefixLenU);
textLen := UINT_TO_INT(LEN(InText));

IF prefixLen <= 0 THEN
    IDECON_StartsWith := TRUE;
ELSIF textLen < prefixLen THEN
    IDECON_StartsWith := FALSE;
ELSE
	// Controlla "prefixLenU" caratteri a partire dalla posizione 1
    IDECON_StartsWith := (MID(InText,  prefixLenU,1) = Prefix);
END_IF;