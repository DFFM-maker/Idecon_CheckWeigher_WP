// ============================================================================
// FUNCTION BLOCK: FB_IDECON_Client
// Description: Client TCP completo per checkweigher Idecon
//
//   Gestisce:
//     - Connessione / riconnessione automatica TCP
//     - Invio MSGFILTER=23 a connessione stabilita
//     - Ricezione non-bloccante (TimeOut=0, nessun falso errore 0x0400)
//     - Buffer di accumulo con parsing STX/ETX
//     - Dispatcher: WEIGHT / EVENT / STATSV / STATP / MSGFILTER / NEWPIECE
//     - Decodifica bitmap classificazione (19 bit) in flag BOOL
//     - Statistiche locali Welford running (media, stddev, contatori per classe)
//     - Watchdog RX 60s con riconnessione automatica
//     - Gestione comando generico (IdeconInterface.Cmd)
//
//   FIX inclusi:
//     #1 TimeOut=0  -> nessun falso bRcvError 0x0400
//     #2 bNeedRcvRestart -> gap ricezione ridotto a 1 scan
//     #3 State 99   -> reset FB ricezione, buffer, CmdSent
//
// Uso nel main:
//     fbIdecon(Enable := MachineAnalytics.HMI_Interface.weigher_Idecon,
//              Reset  := bResetStats);
//
// Struttura esterna richiesta:
//     IdeconInterface : DT_IdeconInterface  (VAR_EXTERNAL / GLOBAL)
// ============================================================================


// ============================================================================
// INIZIO CORPO FB
// ============================================================================

// --- RESET STATISTICHE (fronte di salita su Reset) ---
IF Reset AND NOT bResetPrev THEN
    IdeconInterface.Stats.TotalWeights      := UDINT#0;
    IdeconInterface.Stats.TotalAccepted     := UDINT#0;
    IdeconInterface.Stats.TotalRejected     := UDINT#0;
    IdeconInterface.Stats.TotalExpelled     := UDINT#0;
    IdeconInterface.Stats.CountOK           := UDINT#0;
    IdeconInterface.Stats.CountOKPlus       := UDINT#0;
    IdeconInterface.Stats.CountOKMinus      := UDINT#0;
    IdeconInterface.Stats.CountPlus         := UDINT#0;
    IdeconInterface.Stats.CountPlusPlus     := UDINT#0;
    IdeconInterface.Stats.CountMinus        := UDINT#0;
    IdeconInterface.Stats.CountMinusMinus   := UDINT#0;
    IdeconInterface.Stats.CountMetal        := UDINT#0;
    IdeconInterface.Stats.SumWeight_g       := 0.0;
    IdeconInterface.Stats.AvgWeight_g       := 0.0;
    IdeconInterface.Stats.MinWeight_g       := 0.0;
    IdeconInterface.Stats.MaxWeight_g       := 0.0;
    IdeconInterface.Stats.Welford_Mean      := 0.0;
    IdeconInterface.Stats.Welford_M2        := 0.0;
    IdeconInterface.Stats.Welford_Count     := UDINT#0;
    IdeconInterface.Stats.StdDeviation_g    := 0.0;
    IdeconInterface.Stats.FirstWeightTime   := LINT#0;
    IdeconInterface.Stats.LastWeightTime    := LINT#0;
    IdeconInterface.Stats.ProductionTime_sec:= UDINT#0;
    Debug_LogIdx                            := UINT#0;
END_IF;
bResetPrev := Reset;

// --- DISABILITAZIONE ---
IF NOT Enable THEN
    IdeconInterface.Config.Connect  := FALSE;
    IdeconInterface.Initialized     := FALSE;
    Active  := FALSE;
    Error   := FALSE;
    ErrorID := WORD#0;
END_IF;

// --- AVVIO INIZIALIZZAZIONE ---
IF Enable AND NOT IdeconInterface.Initialized THEN
    InitDone        := FALSE;
    i_Loop          := 0;
    State           := 0;
    Connected       := FALSE;
    CmdSent         := FALSE;
    bNeedRcvRestart := FALSE;
    bRcvExecute     := FALSE;
    RxBufLen        := UINT#0;
    RxTotalBytes    := UDINT#0;
    LastRxCount     := UDINT#0;
IdeconInterface.Config.IpAddress := '172.16.224.210';
IdeconInterface.Config.TcpPort   := UINT#50000;
    IdeconInterface.Initialized         := TRUE;
    IdeconInterface.Config.Connect      := TRUE;
    IdeconInterface.Config.MsgFilterValue := UINT#23;
    IdeconInterface.Comm.Connected      := FALSE;
    IdeconInterface.Comm.Online         := FALSE;
    IdeconInterface.Comm.Ready          := FALSE;
    IdeconInterface.SystemError         := FALSE;
    IdeconInterface.Version             := UINT#100;    // v1.00
END_IF;

// --- RESET COMPLETO (Connect=FALSE da HMI) ---
IF NOT IdeconInterface.Config.Connect THEN
    fbClose(Execute := TRUE, Socket := SocketHandle);
    fbTcpConnect(Execute := FALSE);
    fbSocketRcv(
        Execute  := FALSE,
        RcvDat   := RxChunk[0],
        Done     => bRcvDone,
        Busy     => bRcvBusy,
        Error    => bRcvError,
        ErrorID  => wRcvErrorID,
        RcvSize  => RxChunkLen
    );
    bRcvExecute     := FALSE;
    bNeedRcvRestart := FALSE;

    IF fbClose.Done OR fbClose.Error THEN
        fbClose(Execute := FALSE);
        Connected       := FALSE;
        State           := 0;
        InitDone        := FALSE;
        IdeconInterface.Comm.Connected  := FALSE;
        IdeconInterface.Comm.Online     := FALSE;
        IdeconInterface.Comm.Ready      := FALSE;
        bConnectDone    := FALSE;
    END_IF;
    RETURN;
END_IF;

// --- INIZIALIZZAZIONE SOCKET (chiude eventuale socket precedente) ---
IF NOT InitDone THEN
    i_Loop := i_Loop + 1;
    fbClose(Execute := TRUE, Socket := SocketHandle);

    IF fbClose.Done OR fbClose.Error OR i_Loop >= 625 THEN
        fbClose(Execute := FALSE);
        InitDone    := TRUE;
        State       := 0;
        i_Loop      := 0;
    END_IF;
    RETURN;
END_IF;

// ============================================================================
// STATE MACHINE PRINCIPALE
// ============================================================================
CASE State OF

    // -------------------------------------------------------------------------
    0: // CONNESSIONE TCP
    // -------------------------------------------------------------------------
    fbTcpConnect(
        Execute    := TRUE,
        DstAdr     := IdeconInterface.Config.IpAddress,
        DstTcpPort := IdeconInterface.Config.TcpPort,
        SrcTcpPort := UINT#0,
        Socket     => SocketHandle,
        Done       => bConnectDone,
        Busy       => bConnectBusy,
        Error      => bConnectError,
        ErrorID    => wConnectErrorID
    );

    IF bConnectDone THEN
        fbTcpConnect(Execute := FALSE);
        Connected       := TRUE;
        State           := 1;
        CmdSent         := FALSE;
        SendActive      := FALSE;
        SendTimeout     := 0;
        RxBufLen        := UINT#0;
        bRcvExecute     := FALSE;
        bNeedRcvRestart := FALSE;
        LastRxCount     := UDINT#0;
        RxTotalBytes    := UDINT#0;
        IdeconInterface.Comm.Connected      := TRUE;
        IdeconInterface.Comm.RetryCount     := UINT#0;

    ELSIF bConnectError THEN
        ErrorID                             := wConnectErrorID;
        IdeconInterface.Comm.LastError      := wConnectErrorID;
        IdeconInterface.Comm.ErrorCount     := IdeconInterface.Comm.ErrorCount + UDINT#1;
        State := 99;
    END_IF;

    // -------------------------------------------------------------------------
    1: // ONLINE - RICEZIONE E PARSING
    // -------------------------------------------------------------------------

    // Reset valid flags ogni scan (vengono rialzati solo se arriva dato in questo scan)
    IdeconInterface.LastEvent.Valid  := FALSE;
    IdeconInterface.LastWeight.Valid := FALSE;

    // --- INVIO MSGFILTER ---
    IF NOT CmdSent THEN
        IF NOT SendActive THEN
            TxBuffer[0]  := BYTE#16#02; // STX
            TxBuffer[1]  := BYTE#16#4D; // M
            TxBuffer[2]  := BYTE#16#53; // S
            TxBuffer[3]  := BYTE#16#47; // G
            TxBuffer[4]  := BYTE#16#46; // F
            TxBuffer[5]  := BYTE#16#49; // I
            TxBuffer[6]  := BYTE#16#4C; // L
            TxBuffer[7]  := BYTE#16#54; // T
            TxBuffer[8]  := BYTE#16#45; // E
            TxBuffer[9]  := BYTE#16#52; // R
            TxBuffer[10] := BYTE#16#3D; // =
            // Valore filtro dal config (default 23 = "32" "33")
            TxBuffer[11] := BYTE#16#32; // 2
            TxBuffer[12] := BYTE#16#33; // 3
            TxBuffer[13] := BYTE#16#03; // ETX
            SendActive   := TRUE;
            SendTimeout  := 0;
            IdeconInterface.Comm.TxCount := IdeconInterface.Comm.TxCount + UDINT#1;
        ELSE
            SendTimeout := SendTimeout + 1;
        END_IF;
    END_IF;

    fbSocketSend(
        Execute  := SendActive,
        Socket   := SocketHandle,
        SendDat  := TxBuffer[0],
        Size     := UINT#14,
        Done     => bSendDone,
        Busy     => bSendBusy,
        Error    => bSendError,
        ErrorID  => wSendErrorID
    );

    IF SendActive THEN
        IF bSendDone OR bSendError OR (SendTimeout > 500) THEN
            SendActive := FALSE;
            CmdSent    := TRUE;
            IF bSendError THEN
                ErrorID                         := wSendErrorID;
                IdeconInterface.Comm.LastError  := wSendErrorID;
            END_IF;
        END_IF;
    END_IF;

    // =========================================================================
    // FIX #1 + #2: AUTOTRIGGER RICEZIONE NON-BLOCCANTE
    // TimeOut=0  -> Done immediato con o senza dati, mai bRcvError per timeout
    // bNeedRcvRestart -> gap ridotto a 1 scan dopo ogni Done/Error
    // =========================================================================
    IF bRcvDone OR bRcvError THEN
        bRcvExecute     := FALSE;
        // ErrorID benigni (non devono fermare la ricezione né andare a State 99):
        //   0x0400 = Timeout (SktTCPRcv con TimeOut>0, nessun dato nel periodo)
        //   0x2006 = Buffer vuoto (SktTCPRcv con TimeOut=0, connessione viva ma no dati)
        // Entrambi devono riavviare la ricezione normalmente.
        // Solo errori "reali" (es. 0x2003=reset connessione) fermano e vanno a State 99.
        bNeedRcvRestart := NOT (bRcvError
                                AND wRcvErrorID <> WORD#16#0400
                                AND wRcvErrorID <> WORD#16#2006);
        // Contatore soft-error per diagnostica (non bloccante)
        IF bRcvError AND (wRcvErrorID = WORD#16#0400 OR wRcvErrorID = WORD#16#2006) THEN
            Debug_RcvSoftErrCount := Debug_RcvSoftErrCount + UDINT#1;
        END_IF;
    ELSIF bNeedRcvRestart AND NOT bRcvBusy THEN
        bRcvExecute     := TRUE;
        bNeedRcvRestart := FALSE;
    ELSIF NOT bRcvBusy AND NOT bRcvExecute THEN
        bRcvExecute := TRUE;
    END_IF;

    fbSocketRcv(
        Execute  := bRcvExecute,
        Socket   := SocketHandle,
        TimeOut  := UINT#0,         // FIX #1: non-bloccante
        Size     := UINT#512,
        RcvDat   := RxChunk[0],
        Done     => bRcvDone,
        Busy     => bRcvBusy,
        Error    => bRcvError,
        ErrorID  => wRcvErrorID,
        RcvSize  => RxChunkLen
    );

    // --- ACCUMULO BUFFER ---
    IF bRcvDone AND RxChunkLen > UINT#0 THEN
        RxTotalBytes    := RxTotalBytes + UDINT_TO_UINT(RxChunkLen);
        IdeconInterface.Comm.RxCount           := IdeconInterface.Comm.RxCount + UDINT#1;
        IdeconInterface.Comm.RxTotalByteCount  := RxTotalBytes;

        IF (RxBufLen + RxChunkLen) <= UINT#2048 THEN
            FOR ix := UINT#0 TO RxChunkLen - UINT#1 DO
                RxBuf[RxBufLen + ix] := RxChunk[ix];
            END_FOR;
            RxBufLen := RxBufLen + RxChunkLen;
        ELSE
            // Overflow buffer: flush e ricomincia (evita blocco)
            RxBufLen := UINT#0;
            IdeconInterface.Stats.OtherErrors_Count := IdeconInterface.Stats.OtherErrors_Count + UDINT#1;
        END_IF;
    END_IF;

    // =========================================================================
    // PARSING LOOP: estrae frame STX...ETX dal buffer
    // =========================================================================
    WHILE RxBufLen > UINT#2 DO
        stxPos := -1;
        etxPos := -1;

        // Cerca STX (0x02)
        FOR ix := UINT#0 TO RxBufLen - UINT#1 DO
            IF RxBuf[ix] = BYTE#16#02 THEN
                stxPos := UINT_TO_INT(ix);
                EXIT;
            END_IF;
        END_FOR;

        // Cerca ETX (0x03) dopo STX
        IF stxPos >= 0 THEN
            FOR ix := UINT#0 TO RxBufLen - UINT#1 DO
                IF RxBuf[ix] = BYTE#16#03 AND UINT_TO_INT(ix) > stxPos THEN
                    etxPos := UINT_TO_INT(ix);
                    EXIT;
                END_IF;
            END_FOR;
        END_IF;

        IF stxPos >= 0 AND etxPos > stxPos THEN
            // Frame completo trovato
            payloadLen := INT_TO_UINT(etxPos - stxPos - 1);

            // Copia payload in tempBytes
            FOR ix := UINT#0 TO payloadLen - UINT#1 DO
                j := UINT_TO_INT(stxPos) + 1 + UINT_TO_INT(ix);
                IF j < 2048 THEN tempBytes[ix] := RxBuf[j]; END_IF;
            END_FOR;

            // Converti in stringa
            tempStr := AryToString(tempBytes[0], payloadLen);

            // =================================================================
            // DISPATCHER MESSAGGI
            // =================================================================

            // 1. WEIGHT
            IF FIND(tempStr, 'WEIGHT=') = 1 THEN
                tempStr := DELETE(tempStr, 7, 1);   // rimuove "WEIGHT="

                // Log debug
                Debug_WeightLog[Debug_LogIdx] := tempStr;
                Debug_LogIdx := Debug_LogIdx + 1;
                IF Debug_LogIdx >= UINT#24 THEN Debug_LogIdx := UINT#0; END_IF;

                // Reset struttura
                IdeconInterface.LastWeight.ParseError := FALSE;

                // Parsing campi separati da '|'
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.Timestamp := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.ProductionOrder := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.BatchCode := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.RecipeName := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.LineCode := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.LastWeight.SerialNumber := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;

                pos := FIND(tempStr, '|');
                IF pos > 0 THEN
                    fieldStr := LEFT(tempStr, pos-1);
                    IF LEN(fieldStr) > 0 THEN IdeconInterface.LastWeight.WeightMg := STRING_TO_DINT(fieldStr); END_IF;
                    tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1);
                END_IF;

                pos := FIND(tempStr, '|');
                IF pos > 0 THEN
                    fieldStr := LEFT(tempStr, pos-1);
                    IF LEN(fieldStr) > 0 THEN IdeconInterface.LastWeight.DeltaMg := STRING_TO_DINT(fieldStr); END_IF;
                    tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1);
                END_IF;

                // Classification (ultimo campo, senza '|' finale)
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN fieldStr := LEFT(tempStr, pos-1); ELSE fieldStr := tempStr; END_IF;
                IF LEN(fieldStr) > 0 THEN
                    // FIX: Il protocollo Idecon invia Classification in HEX (es: "10480" = 0x10480)
                    // Parser HEX ottimizzato: usa FIND per lookup invece di 16 IF
                    Debug_Weights_classification[Debug_LogIdx] := fieldStr;  // Salva per debug
                    
                    classVal := UDINT#0;
                    
                    // Processa caratteri da sinistra a destra
                    WHILE LEN(fieldStr) > 0 DO
                        tempStr := LEFT(fieldStr, 1);  // Primo carattere
                        
                        // Lookup carattere HEX (0-9 = posizione 1-10, A-F = posizione 11-16)
                        pos := FIND('0123456789ABCDEFabcdef', tempStr);
                        IF pos > 0 AND pos <= 10 THEN
                            h_digit := UINT_TO_UDINT(INT_TO_UINT(pos - 1));  // '0'=pos 1 → digit 0
                        ELSIF pos > 10 AND pos <= 16 THEN
                            h_digit := UINT_TO_UDINT(INT_TO_UINT(pos - 11)) + UDINT#10;  // 'A'=pos 11 → digit 10
                        ELSIF pos > 16 THEN
                            h_digit := UINT_TO_UDINT(INT_TO_UINT(pos - 17)) + UDINT#10;  // 'a'=pos 17 → digit 10
                        ELSE
                            h_digit := UDINT#0;  // Carattere invalido
                        END_IF;
                        
                        classVal := classVal * UDINT#16 + h_digit;
                        fieldStr := DELETE(fieldStr, 1, 1);  // Rimuovi primo carattere
                    END_WHILE;
                    
                    IdeconInterface.LastWeight.Classification := classVal;
                    
                    // Debug log
                    Debug_Weights_classification[Debug_LogIdx] := CONCAT('HEX:', Debug_Weights_classification[Debug_LogIdx]);
                    Debug_Weights_classification[Debug_LogIdx] := CONCAT(Debug_Weights_classification[Debug_LogIdx], ' DEC:');
                    Debug_Weights_classification[Debug_LogIdx] := CONCAT(Debug_Weights_classification[Debug_LogIdx], UDINT_TO_STRING(classVal));

                    // Decodifica bitmap 19 bit
                    // NJ non supporta AND su UDINT -> cast a DWORD
                    classDW := UDINT_TO_DWORD(classVal);
                    IdeconInterface.LastWeight.FlagProductTooLong    := (classDW AND DWORD#16#00001) <> DWORD#0;  // Bit 0
                    IdeconInterface.LastWeight.FlagProductTooShort   := (classDW AND DWORD#16#00002) <> DWORD#0;  // Bit 1
                    IdeconInterface.LastWeight.FlagMetal             := (classDW AND DWORD#16#00004) <> DWORD#0;  // Bit 2
                    IdeconInterface.LastWeight.FlagWeightPlusPlus    := (classDW AND DWORD#16#00008) <> DWORD#0;  // Bit 3
                    IdeconInterface.LastWeight.FlagWeightPlus        := (classDW AND DWORD#16#00010) <> DWORD#0;  // Bit 4
                    IdeconInterface.LastWeight.FlagWeightMinusMinus  := (classDW AND DWORD#16#00020) <> DWORD#0;  // Bit 5
                    IdeconInterface.LastWeight.FlagWeightMinus       := (classDW AND DWORD#16#00040) <> DWORD#0;  // Bit 6
                    IdeconInterface.LastWeight.FlagWeightOK          := (classDW AND DWORD#16#00080) <> DWORD#0;  // Bit 7
                    IdeconInterface.LastWeight.FlagExpelled          := (classDW AND DWORD#16#00100) <> DWORD#0;  // Bit 8
                    IdeconInterface.LastWeight.FlagProductTooClose   := (classDW AND DWORD#16#00200) <> DWORD#0;  // Bit 9
                    IdeconInterface.LastWeight.FlagNewDynamicTare    := (classDW AND DWORD#16#00400) <> DWORD#0;  // Bit 10
                    IdeconInterface.LastWeight.FlagIncorrectTare     := (classDW AND DWORD#16#00800) <> DWORD#0;  // Bit 11
                    IdeconInterface.LastWeight.FlagAboveMaxCapacity  := (classDW AND DWORD#16#01000) <> DWORD#0;  // Bit 12
                    IdeconInterface.LastWeight.FlagBelowMinCapacity  := (classDW AND DWORD#16#02000) <> DWORD#0;  // Bit 13
                    IdeconInterface.LastWeight.FlagOKMinusAccepted   := (classDW AND DWORD#16#04000) <> DWORD#0;  // Bit 14
                    IdeconInterface.LastWeight.FlagNoUpstreamConsent := (classDW AND DWORD#16#08000) <> DWORD#0;  // Bit 15
                    IdeconInterface.LastWeight.FlagInvalidPreweight  := (classDW AND DWORD#16#10000) <> DWORD#0;  // Bit 16
                    IdeconInterface.LastWeight.FlagOKAboveNominal    := (classDW AND DWORD#16#20000) <> DWORD#0;  // Bit 17
                    IdeconInterface.LastWeight.FlagOKBelowNominal    := (classDW AND DWORD#16#40000) <> DWORD#0;  // Bit 18
                END_IF;

                IdeconInterface.LastWeight.Valid := TRUE;

                // =============================================================
                // STATISTICHE LOCALI
                // =============================================================
                wf_weight_g := DINT_TO_REAL(IdeconInterface.LastWeight.WeightMg) / 1000.0;

                IdeconInterface.Stats.TotalWeights := IdeconInterface.Stats.TotalWeights + UDINT#1;
                IdeconInterface.Stats.SumWeight_g  := IdeconInterface.Stats.SumWeight_g + wf_weight_g;

                // Min/Max
                IF IdeconInterface.Stats.TotalWeights = UDINT#1 THEN
                    IdeconInterface.Stats.MinWeight_g := wf_weight_g;
                    IdeconInterface.Stats.MaxWeight_g := wf_weight_g;
                ELSE
                    IF wf_weight_g < IdeconInterface.Stats.MinWeight_g THEN
                        IdeconInterface.Stats.MinWeight_g := wf_weight_g;
                    END_IF;
                    IF wf_weight_g > IdeconInterface.Stats.MaxWeight_g THEN
                        IdeconInterface.Stats.MaxWeight_g := wf_weight_g;
                    END_IF;
                END_IF;

                // Welford online algorithm (numericamente stabile)
                IdeconInterface.Stats.Welford_Count := IdeconInterface.Stats.Welford_Count + UDINT#1;
                wf_delta   := wf_weight_g - IdeconInterface.Stats.Welford_Mean;
                IdeconInterface.Stats.Welford_Mean  := IdeconInterface.Stats.Welford_Mean
                                                       + wf_delta / UDINT_TO_REAL(IdeconInterface.Stats.Welford_Count);
                wf_delta2  := wf_weight_g - IdeconInterface.Stats.Welford_Mean;
                IdeconInterface.Stats.Welford_M2    := IdeconInterface.Stats.Welford_M2
                                                       + wf_delta * wf_delta2;

                IF IdeconInterface.Stats.Welford_Count > UDINT#1 THEN
                    wf_variance := IdeconInterface.Stats.Welford_M2
                                   / UDINT_TO_REAL(IdeconInterface.Stats.Welford_Count - UDINT#1);
                    IF wf_variance > 0.0 THEN
                        IdeconInterface.Stats.StdDeviation_g := SQRT(wf_variance);
                    ELSE
                        IdeconInterface.Stats.StdDeviation_g := 0.0;
                    END_IF;
                END_IF;

                IdeconInterface.Stats.AvgWeight_g := IdeconInterface.Stats.SumWeight_g
                                                      / UDINT_TO_REAL(IdeconInterface.Stats.TotalWeights);

                // Contatori per classe (bitmap)
                // Priorità: FlagWeightOK → accettata | FlagOKMinusAccepted → accettata (bit14) | else → rifiutata
                // Nota: FlagIncorrectTare (bit11) è solo informativo - la pesata è già classificata da altri bit
                IF IdeconInterface.LastWeight.FlagWeightOK THEN
                    // Bit 7: peso in fascia OK
                    IF IdeconInterface.LastWeight.FlagOKAboveNominal THEN
                        IdeconInterface.Stats.CountOKPlus   := IdeconInterface.Stats.CountOKPlus + UDINT#1;
                    ELSIF IdeconInterface.LastWeight.FlagOKBelowNominal THEN
                        IdeconInterface.Stats.CountOKMinus  := IdeconInterface.Stats.CountOKMinus + UDINT#1;
                    ELSE
                        IdeconInterface.Stats.CountOK       := IdeconInterface.Stats.CountOK + UDINT#1;
                    END_IF;
                    IdeconInterface.Stats.TotalAccepted := IdeconInterface.Stats.TotalAccepted + UDINT#1;
                ELSIF IdeconInterface.LastWeight.FlagOKMinusAccepted THEN
                    // Bit 14: accettata senza FlagWeightOK (n% OK-, media errore >0, ecc.)
                    // L'Idecon la mostra come "ok" ma non imposta FlagWeightOK
                    IdeconInterface.Stats.CountOKMinus  := IdeconInterface.Stats.CountOKMinus + UDINT#1;
                    IdeconInterface.Stats.TotalAccepted := IdeconInterface.Stats.TotalAccepted + UDINT#1;
                ELSE
                    // Nessun flag di accettazione: rifiutata
                    IdeconInterface.Stats.TotalRejected := IdeconInterface.Stats.TotalRejected + UDINT#1;
                    IF IdeconInterface.LastWeight.FlagWeightPlusPlus THEN
                        IdeconInterface.Stats.CountPlusPlus    := IdeconInterface.Stats.CountPlusPlus + UDINT#1;
                    ELSIF IdeconInterface.LastWeight.FlagWeightPlus THEN
                        IdeconInterface.Stats.CountPlus        := IdeconInterface.Stats.CountPlus + UDINT#1;
                    ELSIF IdeconInterface.LastWeight.FlagWeightMinusMinus THEN
                        IdeconInterface.Stats.CountMinusMinus  := IdeconInterface.Stats.CountMinusMinus + UDINT#1;
                    ELSIF IdeconInterface.LastWeight.FlagWeightMinus THEN
                        IdeconInterface.Stats.CountMinus       := IdeconInterface.Stats.CountMinus + UDINT#1;
                    END_IF;
                END_IF;

                IF IdeconInterface.LastWeight.FlagExpelled THEN
                    IdeconInterface.Stats.TotalExpelled := IdeconInterface.Stats.TotalExpelled + UDINT#1;
                END_IF;
                IF IdeconInterface.LastWeight.FlagMetal THEN
                    IdeconInterface.Stats.CountMetal    := IdeconInterface.Stats.CountMetal + UDINT#1;
                END_IF;

            // 2. EVENT
            ELSIF FIND(tempStr, 'EVENT=') = 1 THEN
                tempStr := DELETE(tempStr, 6, 1);   // rimuove "EVENT="
                IdeconInterface.LastEvent.EventDescription  := tempStr;
                IdeconInterface.LastEvent.Valid             := TRUE;

                // Classificazione evento da codice numerico (primo campo)
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN fieldStr := LEFT(tempStr, pos-1); ELSE fieldStr := tempStr; END_IF;
                IF LEN(fieldStr) > 0 THEN
                    IdeconInterface.LastEvent.EventCode := STRING_TO_UINT(fieldStr);
                    // Convenzione Idecon: 1000-1999=Info, 2000-2999=Warning, 3000+=Error
                    IdeconInterface.LastEvent.IsInfo    := IdeconInterface.LastEvent.EventCode < UINT#2000;
                    IdeconInterface.LastEvent.IsWarning := IdeconInterface.LastEvent.EventCode >= UINT#2000
                                                          AND IdeconInterface.LastEvent.EventCode < UINT#3000;
                    IdeconInterface.LastEvent.IsError   := IdeconInterface.LastEvent.EventCode >= UINT#3000;
                END_IF;

            // 3. STATSV (stato macchina: 8 caratteri binari)
            ELSIF FIND(tempStr, 'STATSV=') = 1 THEN
                tempStr := DELETE(tempStr, 7, 1);   // rimuove "STATSV="
                // Il campo status è il testo dopo "STATSV=", es. "20110011"
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN fieldStr := LEFT(tempStr, pos-1); ELSE fieldStr := tempStr; END_IF;
                IF LEN(fieldStr) >= 8 THEN
                    IdeconInterface.Status.StatusCode       := LEFT(fieldStr, 8);
                    IdeconInterface.Comm.StatusCode         := LEFT(fieldStr, 8);
                    // Bit 0: MotorStatus (char 1)
                    IdeconInterface.Status.MotorStatus      := STRING_TO_UINT(MID(fieldStr, 1, 1));
                    IdeconInterface.Status.MotorRunning     := IdeconInterface.Status.MotorStatus > UINT#0
                                                              AND IdeconInterface.Status.MotorStatus <> UINT#3;
                    // Bit 2: ProductionStarted (char 3)
                    IdeconInterface.Status.ProductionStarted := MID(fieldStr, 1, 3) = '1';
                    // Bit 4: HasErrors (char 5)
                    IdeconInterface.Status.HasErrors        := MID(fieldStr, 1, 5) = '1';
                    // Bit 5: HasWarnings (char 6)
                    IdeconInterface.Status.HasWarnings      := MID(fieldStr, 1, 6) = '1';
                    // Bit 6: HasMessages (char 7)
                    IdeconInterface.Status.HasMessages      := MID(fieldStr, 1, 7) = '1';
                    // Bit 7: StatsEnabled (char 8)
                    IdeconInterface.Status.StatsEnabled     := MID(fieldStr, 1, 8) = '1';
                    IdeconInterface.Status.Valid            := TRUE;
                END_IF;
                // WorkMode (secondo campo dopo '|')
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN
                    tempStr  := DELETE(tempStr, INT_TO_UINT(pos), 1);
                    pos      := FIND(tempStr, '|');
                    IF pos > 0 THEN fieldStr := LEFT(tempStr, pos-1); ELSE fieldStr := tempStr; END_IF;
                    IF LEN(fieldStr) > 0 THEN
                        IdeconInterface.Status.WorkMode     := STRING_TO_UINT(fieldStr);
                        IdeconInterface.Comm.WorkMode       := IdeconInterface.Status.WorkMode;
                        IdeconInterface.Status.IsLocalMode  := IdeconInterface.Status.WorkMode = UINT#1;
                        IdeconInterface.Status.IsRemoteMode := IdeconInterface.Status.WorkMode = UINT#2;
                        IdeconInterface.Status.IsMaintenanceMode := IdeconInterface.Status.WorkMode = UINT#3;
                        IdeconInterface.Comm.IsLocalMode    := IdeconInterface.Status.IsLocalMode;
                        IdeconInterface.Comm.IsRemoteMode   := IdeconInterface.Status.IsRemoteMode;
                        IdeconInterface.Comm.IsMaintenanceMode := IdeconInterface.Status.IsMaintenanceMode;
                    END_IF;
                END_IF;

            // 4. STATP (statistiche batch dalla bilancia)
            ELSIF FIND(tempStr, 'STATP=') = 1 THEN
                tempStr := DELETE(tempStr, 6, 1);   // rimuove "STATP="
                // Parsing dei campi principali (in ordine da protocollo)
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.Timestamp := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.BatchStartTime := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.ProductionOrder := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.ProductionCode := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.RecipeName := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.LineCode := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN IdeconInterface.BatchStats.SerialNumber := LEFT(tempStr, pos-1); tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1); END_IF;
                // Campo 8: TotalProducts
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN
                    fieldStr := LEFT(tempStr, pos-1);
                    IF LEN(fieldStr) > 0 THEN IdeconInterface.BatchStats.TotalProducts := STRING_TO_UDINT(fieldStr); END_IF;
                    tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1);
                END_IF;
                // Campo 9: TotalAccepted
                pos := FIND(tempStr, '|');
                IF pos > 0 THEN
                    fieldStr := LEFT(tempStr, pos-1);
                    IF LEN(fieldStr) > 0 THEN IdeconInterface.BatchStats.TotalAccepted := STRING_TO_UDINT(fieldStr); END_IF;
                    tempStr := DELETE(tempStr, INT_TO_UINT(pos), 1);
                END_IF;
                // Calcola yield se possibile
                IF IdeconInterface.BatchStats.TotalProducts > UDINT#0 THEN
                    IdeconInterface.BatchStats.YieldPercentage :=
                        UDINT_TO_REAL(IdeconInterface.BatchStats.TotalAccepted)
                        / UDINT_TO_REAL(IdeconInterface.BatchStats.TotalProducts) * 100.0;
                END_IF;
                IdeconInterface.BatchStats.DataValid    := TRUE;

            // 5. MSGFILTER / NEWPIECE (ignorati, solo ACK)
            ELSIF FIND(tempStr, 'MSGFILTER=') = 1 OR FIND(tempStr, 'NEWPIECE') = 1 THEN
                ;   // nessuna azione

            END_IF;

            // =================================================================
            // SHIFT BUFFER: rimuove il frame processato
            // =================================================================
            j := INT_TO_UINT(etxPos) + UINT#1;
            IF j < RxBufLen THEN
                FOR idxShift := UINT#0 TO (RxBufLen - j) - UINT#1 DO
                    RxBuf[idxShift] := RxBuf[j + idxShift];
                END_FOR;
                RxBufLen := RxBufLen - j;
            ELSE
                RxBufLen := UINT#0;
            END_IF;

        ELSE
            EXIT;   // Frame incompleto: aspetta prossimo chunk
        END_IF;
    END_WHILE;

    // --- GESTIONE COMANDO GENERICO (IdeconInterface.Cmd) ---
    // Fronte di salita su Cmd.Execute: invia Cmd.Command alla bilancia
    IF IdeconInterface.Cmd.Execute AND NOT IdeconInterface.Cmd.Busy
       AND NOT IdeconInterface.Cmd.Done AND CmdSent THEN
        IF NOT SendActive THEN
            // Costruisce frame STX + Command + ETX
            TxBuffer[0] := BYTE#16#02;
            FOR ix := UINT#0 TO INT_TO_UINT(LEN(IdeconInterface.Cmd.Command)) - UINT#1 DO
                TxBuffer[ix + UINT#1] := STRING_TO_BYTE(MID(IdeconInterface.Cmd.Command, 1, UINT_TO_INT(ix) + 1));
            END_FOR;
            TxBuffer[INT_TO_UINT(LEN(IdeconInterface.Cmd.Command)) + UINT#1] := BYTE#16#03;
            SendActive := TRUE;
            SendTimeout := 0;
            IdeconInterface.Cmd.Busy := TRUE;
            IdeconInterface.Cmd.Done := FALSE;
            IdeconInterface.Cmd.Error := FALSE;
            IdeconInterface.Comm.TxCount := IdeconInterface.Comm.TxCount + UDINT#1;
        END_IF;
    END_IF;

    // Completamento comando
    IF IdeconInterface.Cmd.Busy AND bSendDone THEN
        IdeconInterface.Cmd.Busy := FALSE;
        IdeconInterface.Cmd.Done := TRUE;
    END_IF;
    IF IdeconInterface.Cmd.Busy AND bSendError THEN
        IdeconInterface.Cmd.Busy    := FALSE;
        IdeconInterface.Cmd.Error   := TRUE;
        IdeconInterface.Cmd.ErrorID := WORD_TO_UDINT(wSendErrorID);
    END_IF;

    // --- WATCHDOG RX (60s senza dati → riconnetti) ---
    IF IdeconInterface.Comm.RxCount <> LastRxCount THEN
        LastRxCount := IdeconInterface.Comm.RxCount;
        tonWatchdog(IN := FALSE);
    ELSE
        tonWatchdog(IN := TRUE, PT := T#60S);
        IF tonWatchdog.Q THEN
            tonWatchdog(IN := FALSE);
            Connected := FALSE;
            // Diagnostica: registra motivo State 99
            Debug_State99Reason  := UINT#1;   // 1 = Watchdog 60s
            Debug_State99ErrorID := WORD#0;
            Debug_State99Count   := Debug_State99Count + UDINT#1;
            Debug_WdogFireCount  := Debug_WdogFireCount + UDINT#1;
            State := 99;
        END_IF;
    END_IF;

    // --- GESTIONE ERRORI ---
    // NOTA: 0x0400 (timeout) e 0x2006 (buffer vuoto non-bloccante) sono errori benigni:
    //       indicano assenza di dati ma connessione viva. Non devono andare a State 99.
    //       Solo errori "reali" (connessione chiusa/resettata dal remoto, ecc.) vanno a 99.
    IF bConnectError OR (bRcvError
                         AND wRcvErrorID <> WORD#16#0400
                         AND wRcvErrorID <> WORD#16#2006) THEN
        Connected := FALSE;
        IF bConnectError THEN
            ErrorID := wConnectErrorID;
            Debug_State99Reason := UINT#3;    // 3 = ConnectError
        ELSE
            ErrorID := wRcvErrorID;
            Debug_State99Reason := UINT#2;    // 2 = RcvError reale
        END_IF;
        // Diagnostica: registra motivo e ErrorID
        Debug_State99ErrorID := ErrorID;
        Debug_State99Count   := Debug_State99Count + UDINT#1;
        IdeconInterface.Comm.LastError      := ErrorID;
        IdeconInterface.Comm.ErrorCount     := IdeconInterface.Comm.ErrorCount + UDINT#1;
        State := 99;
    END_IF;

    // -------------------------------------------------------------------------
    99: // ERRORE / RICONNESSIONE
    // -------------------------------------------------------------------------
    Error := TRUE;

    // FIX #3: reset completo FB ricezione
    fbTcpConnect(Execute := FALSE);
    bRcvExecute     := FALSE;
    bNeedRcvRestart := FALSE;

    fbSocketRcv(
        Execute  := FALSE,
        RcvDat   := RxChunk[0],
        Done     => bRcvDone,
        Busy     => bRcvBusy,
        Error    => bRcvError,
        ErrorID  => wRcvErrorID,
        RcvSize  => RxChunkLen
    );

    // Chiusura socket: Execute attivo finché non arriva Done o Error
    fbClose(Execute := NOT fbClose.Done AND NOT fbClose.Error, Socket := SocketHandle);

    IF fbClose.Done OR fbClose.Error THEN
        // Reset stato (idempotente: sicuro se eseguito più volte)
        Connected                       := FALSE;
        IdeconInterface.Comm.Connected  := FALSE;
        IdeconInterface.Comm.Online     := FALSE;
        IdeconInterface.Comm.Ready      := FALSE;
        RxBufLen                        := UINT#0;  // FIX #3: flush buffer
        CmdSent                         := FALSE;   // FIX #3: reinvia MSGFILTER
    END_IF;

    // Timer riconnessione FUORI dal blocco fbClose.Done:
    // deve essere chiamato ogni scan altrimenti si resetta
    tonReconnect(IN := TRUE, PT := T#10S);
    IF tonReconnect.Q THEN
        tonReconnect(IN := FALSE);
        fbClose(Execute := FALSE);  // reset esplicito fbClose per prossimo uso
        IdeconInterface.Comm.RetryCount := IdeconInterface.Comm.RetryCount + UINT#1;
        Error := FALSE;
        State := 0;
    END_IF;

END_CASE;

// ============================================================================
// OUTPUT FINALI
// ============================================================================
IdeconInterface.Comm.Online     := Connected AND (State = 1);
IdeconInterface.Comm.Ready      := (State = 1) AND CmdSent;
Active                          := IdeconInterface.Comm.Online;
IdeconInterface.SystemError     := bConnectError
                                   OR (bRcvError
                                       AND wRcvErrorID <> WORD#16#0400
                                       AND wRcvErrorID <> WORD#16#2006);