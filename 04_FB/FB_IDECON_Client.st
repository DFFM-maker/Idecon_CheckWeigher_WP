// ==============================================================================
// FUNCTION BLOCK: FB_IDECON_Client
// DESCRIZIONE: Driver Protocollo Idecon.
//              - Gestisce Buffer circolare di ricezione
//              - Riconosce messaggi (STX...ETX)
//              - Parsa stringhe (STATSV, WEIGHT, STATP)
//              - Serializza comandi in uscita
//              - Filtra messaggi spuri (NEWPIECE)
// ==============================================================================

// --- RESET VARIABILI ---
IF NOT Enable THEN
    Error := FALSE;
    ErrorId := 0;
    RxLen := 0;
    cmdPending := FALSE;
    HasMessage := FALSE;
    Weight.Valid := FALSE;
    StatP.Valid := FALSE;
    TxOutValid := FALSE;
    TxOutLen := 0;
    prevEnable := FALSE;
    prevCommandTrigger := FALSE;
    RETURN;
END_IF;

// --- INIZIALIZZAZIONE ---
// All'abilitazione, invia comando per impostare filtro messaggi
IF (Enable AND NOT prevEnable) THEN
    RxLen := 0;
    cmdPending := TRUE;
    cmdQueue := CONCAT('MSGFILTER=', UINT_TO_STRING(MsgFilter));
END_IF;
prevEnable := Enable;

// --- CODA COMANDI ---
// Se arriva un trigger di comando esterno, mettilo in coda
IF (CommandTrigger AND NOT prevCommandTrigger) THEN
    IF NOT cmdPending THEN
        cmdPending := TRUE;
        cmdQueue := Command;
    END_IF;
END_IF;
prevCommandTrigger := CommandTrigger;

// --- GESTIONE TRASMISSIONE (SERIALIZZAZIONE) ---
// Resetta flag validità se il comando precedente è stato consumato
IF TxOutValid AND TxConsumed THEN
    TxOutValid := FALSE;
    TxOutLen := 0;
END_IF;

// Se c'è un comando pendente e il buffer TX è libero, serializza la stringa
IF (NOT TxOutValid) AND cmdPending THEN
    TxOut[0] := 16#02; // Aggiunge STX (Start of Text)
    TxOutLen := 1;
    
    // Ciclo di conversione carattere per carattere Stringa -> Byte ASCII
    FOR i := 1 TO LEN(cmdQueue) DO
        sTxCh := MID(cmdQueue, 1, i); // Estrae 1 carattere alla posizione i
        
        // Logica di conversione caratteri speciali e alfanumerici
        pos := FIND('0123456789', sTxCh);
        IF pos > 0 THEN
            // Numeri 0-9
            CASE pos OF
                1: TxOut[TxOutLen] := 16#30; 2: TxOut[TxOutLen] := 16#31; 3: TxOut[TxOutLen] := 16#32;
                4: TxOut[TxOutLen] := 16#33; 5: TxOut[TxOutLen] := 16#34; 6: TxOut[TxOutLen] := 16#35;
                7: TxOut[TxOutLen] := 16#36; 8: TxOut[TxOutLen] := 16#37; 9: TxOut[TxOutLen] := 16#38;
                10: TxOut[TxOutLen] := 16#39;
            ELSE TxOut[TxOutLen] := 16#3F; END_CASE;
        ELSE
            pos := FIND('ABCDEFGHIJKLMNOPQRSTUVWXYZ', sTxCh);
            IF pos > 0 THEN
                // Lettere Maiuscole
                TxOut[TxOutLen] := USINT_TO_BYTE(64 + INT_TO_USINT(pos)); 
            ELSE
                pos := FIND('abcdefghijklmnopqrstuvwxyz', sTxCh);
                IF pos > 0 THEN
                    // Lettere Minuscole
                     TxOut[TxOutLen] := USINT_TO_BYTE(96 + INT_TO_USINT(pos));
                // Caratteri Speciali supportati
                ELSIF sTxCh = '=' THEN TxOut[TxOutLen] := 16#3D;
                ELSIF sTxCh = '|' THEN TxOut[TxOutLen] := 16#7C;
                ELSIF sTxCh = '_' THEN TxOut[TxOutLen] := 16#5F;
                ELSIF sTxCh = '-' THEN TxOut[TxOutLen] := 16#2D;
                ELSIF sTxCh = '.' THEN TxOut[TxOutLen] := 16#2E;
                ELSIF sTxCh = ':' THEN TxOut[TxOutLen] := 16#3A;
                ELSIF sTxCh = '/' THEN TxOut[TxOutLen] := 16#2F;
                ELSIF sTxCh = ' ' THEN TxOut[TxOutLen] := 16#20;
                ELSE TxOut[TxOutLen] := 16#3F; // Carattere sconosciuto -> '?'
                END_IF;
            END_IF;
        END_IF;
        TxOutLen := TxOutLen + 1;
    END_FOR;
    
    TxOut[TxOutLen] := 16#03; // Aggiunge ETX (End of Text)
    TxOutLen := TxOutLen + 1;
    TxOutValid := TRUE; // Segnala dati pronti per l'invio
    cmdPending := FALSE;
END_IF;

// --- GESTIONE RICEZIONE (BUFFERING) ---
// Accoda i nuovi dati ricevuti al buffer interno
IF RxInValid AND (RxInLen > 0) THEN
    // Protezione Overflow: Se il buffer è pieno, resetta tutto
    IF (RxLen + RxInLen) > 2048 THEN
        RxLen := 0; 
    END_IF;

    FOR i := 0 TO RxInLen - 1 DO
        RxBuf[RxLen + i] := RxIn[i];
    END_FOR;
    RxLen := RxLen + RxInLen;
END_IF;

// --- RICERCA MESSAGGI COMPLETI ---
stxPos := -1;
etxPos := -1;
IF RxLen > 0 THEN
    FOR i := 0 TO RxLen - 1 DO
        IF (stxPos < 0) AND (RxBuf[i] = 16#02) THEN // Cerca STX
            stxPos := UINT_TO_INT(i);
        ELSIF (stxPos >= 0) AND (RxBuf[i] = 16#03) THEN // Cerca ETX
            etxPos := UINT_TO_INT(i);
            EXIT; // Trovato un messaggio completo
        END_IF;
    END_FOR;
END_IF;

// --- PARSING MESSAGGIO ---
IF (stxPos >= 0) AND (etxPos > stxPos) THEN
    // Calcola lunghezza payload (senza STX/ETX)
    payloadLen := INT_TO_UINT(etxPos - stxPos - 1);
    tempStr := '';
    
    // Converte Payload da Byte Array a Stringa
    IF payloadLen > 0 THEN
        FOR i := 0 TO payloadLen - 1 DO
            rxIdx := INT_TO_UINT(stxPos) + 1 + i;
            tempStr := CONCAT(tempStr, IDECON_AsciiByteToChar(RxBuf[rxIdx]));
        END_FOR;
    END_IF;

    // --- FILTRO MESSAGGI ---
    // Ignora messaggi di disturbo tipo 'NEWPIECE' che sovrascrivono i dati completi
    IF IDECON_StartsWith(tempStr, 'NEWPIECE') THEN
        tempStr := ''; // Scarta messaggio
    ELSE
        // Messaggio valido: Aggiorna uscita LastMessage
        LastMessage := tempStr;
        HasMessage := TRUE;

        // --- PARSING CONTENUTO ---
        
        // 1. STATSV (Stato Macchina)
        IF IDECON_StartsWith(tempStr, 'STATSV=') THEN
            LastSTATSV := MID(tempStr, 8, LEN(tempStr) - 7);
            IF LEN(LastSTATSV) >= 7 THEN
                modeCh := MID(LastSTATSV, 1, 7); // Estrae carattere modo
                IF modeCh = '1' THEN WorkMode := IDECON_WorkMode#Local;
                ELSIF modeCh = '2' THEN WorkMode := IDECON_WorkMode#Remote;
                ELSIF modeCh = '3' THEN WorkMode := IDECON_WorkMode#Maintenance;
                ELSE WorkMode := IDECON_WorkMode#Local;
                END_IF;
            END_IF;

        // 2. WEIGHT (Dati Pesata Completa)
        ELSIF IDECON_StartsWith(tempStr, 'WEIGHT=') THEN
            tempStr := DELETE(tempStr, 7, 1);

            // Formato: timestamp|[order]|[batch]|recipe|line|serial|weight_mg|delta|classification
            // Campi vuoti (order/batch mancanti) vengono gestiti come stringhe vuote
            Weight.DateTimeText     := IDECON_FieldAt(tempStr, 1, '|');
            Weight.ProductionOrder  := IDECON_FieldAt(tempStr, 2, '|');
            Weight.BatchCode        := IDECON_FieldAt(tempStr, 3, '|');
            Weight.RecipeName       := IDECON_FieldAt(tempStr, 4, '|');
            Weight.LineCode         := IDECON_FieldAt(tempStr, 5, '|');
            Weight.SerialNumber     := IDECON_FieldAt(tempStr, 6, '|');

            // Conversione valori numerici (gia in mg)
            Weight.WeightMg         := STRING_TO_DINT(IDECON_FieldAt(tempStr, 7, '|'));
            Weight.DeltaToNominalMg := IDECON_ParseHexDword(IDECON_FieldAt(tempStr, 8, '|'));

            // Conversione Classificazione (Esadecimale)
            Weight.Classification   := IDECON_ParseHexDword(IDECON_FieldAt(tempStr, 9, '|'));

            Weight.Valid := TRUE;

        // 3. STATP (Statistiche Produzione)
        ELSIF IDECON_StartsWith(tempStr, 'STATP=') THEN
            tempStr := DELETE(tempStr, 6, 1); // Rimuovi 'STATP='
            // Estrazione contatori
            StatP.TotalProducts     := STRING_TO_DINT(IDECON_FieldAt(tempStr, 8, '|'));
            StatP.TotalAccepted     := STRING_TO_DINT(IDECON_FieldAt(tempStr, 9, '|'));
            StatP.RejectedMinus     := STRING_TO_DINT(IDECON_FieldAt(tempStr, 13, '|'));
            StatP.RejectedMinusMinus:= STRING_TO_DINT(IDECON_FieldAt(tempStr, 14, '|'));
            StatP.RejectedPlus      := STRING_TO_DINT(IDECON_FieldAt(tempStr, 15, '|'));
            StatP.RejectedPlusPlus  := STRING_TO_DINT(IDECON_FieldAt(tempStr, 16, '|'));
            StatP.CannotBeWeighed   := STRING_TO_DINT(IDECON_FieldAt(tempStr, 17, '|'));
            StatP.MetalCategory     := STRING_TO_DINT(IDECON_FieldAt(tempStr, 18, '|'));
            StatP.Valid := TRUE;
        END_IF;
    END_IF;

    // --- PULIZIA BUFFER (SHIFTING) ---
    // Rimuove i dati già processati dal buffer interno
    readLen := INT_TO_UINT(etxPos) + 1;
    IF readLen < RxLen THEN
        payloadLen := RxLen - readLen;
        IF payloadLen > 0 THEN
            FOR i := 0 TO payloadLen - 1 DO
                RxBuf[i] := RxBuf[readLen + i];
            END_FOR;
        END_IF;
        RxLen := payloadLen;
    ELSE
        RxLen := 0; // Buffer vuoto
    END_IF;
END_IF;