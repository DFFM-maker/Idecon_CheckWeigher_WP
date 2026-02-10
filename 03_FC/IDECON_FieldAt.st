// ==============================================================================
// FUNZIONE: IDECON_FieldAt
// DESCRIZIONE: Estrae un campo da una stringa separata da delimitatori (es. '|')
// NOTA CRITICA: Utilizza sintassi MID(Testo, Lunghezza, Posizione)
// ==============================================================================

// Variabili Interne (Dichiarare in Sysmac):
// i, n, startPos, endPos, curIndex, resultLen : UINT
// sCh : STRING[2]


n := LEN(InText);
startPos := 1;
endPos := 0;
curIndex := 0;

IF Index = 0 THEN
    IDECON_FieldAt := '';
    RETURN;
END_IF;

FOR i := 1 TO n DO
    sCh := MID(InText,1, i);
    IF sCh = Delim THEN
        curIndex := curIndex + 1;
        IF curIndex = Index THEN
            endPos := i - 1;
            EXIT;
        END_IF;
        startPos := i + 1;
    END_IF;
END_FOR;

IF endPos = 0 THEN
    curIndex := curIndex + 1;
    IF curIndex = Index THEN
        endPos := n;
    END_IF;
END_IF;

IF endPos < startPos THEN
    IDECON_FieldAt := '';
    RETURN;
END_IF;

resultLen := endPos - startPos + 1;
IDECON_FieldAt := MID(InText,  resultLen,startPos);