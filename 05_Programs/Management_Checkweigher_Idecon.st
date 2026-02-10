// ==============================================================================
// Management_Checkweigher_Idecon 
// ==============================================================================

// --- 1. RESET INIZIALE E DISABILITAZIONE ---

IF NOT Enable THEN
    Connected := FALSE;
    iRcvState := 0;
    iTestState := 0;
    RxChunkLen := 0;
    RxChunkValid := FALSE;
    TxConsumed := FALSE;
    Command := '';
    CommandTrigger := FALSE;
    G_Idecon_HMI_Cmd.SendTrigger := FALSE; 
    G_Test_Ejector_Start := FALSE;
    G_Test_Ejector_Restore := FALSE;
    prevHmiSend := FALSE;
    tonReconnect(IN := FALSE);
    
    stepInit := 0;
    bInitCloseDone := FALSE;
    
    fbTcpConnect(Execute := FALSE);
    fbClose(Execute := FALSE);
    
    RETURN;
END_IF;

// --- 2. SEQUENZA DI INIZIALIZZAZIONE SICURA ---

CASE stepInit OF
    0: 
        fbClose(Execute := FALSE, Socket := SocketID_Int);
        stepInit := 10;
        
    10: 
        fbClose(Execute := TRUE, Socket := SocketID_Int);
        IF fbClose.Done OR fbClose.Error THEN
            fbClose(Execute := FALSE, Socket := SocketID_Int);
            stepInit := 20;
        END_IF;
        
    20: 
        bInitCloseDone := TRUE;
END_CASE;

IF NOT bInitCloseDone THEN RETURN; END_IF;

// --- 3. GESTIONE CONNESSIONE TCP ---

tmpIpAddress := Config.IpAdr;
tmpPort := Config.PortNo;

tonReconnect(IN := (NOT Connected AND bConnectError), PT := T#5S);
bEnableConnect := (Enable AND NOT Connected AND NOT bConnectError) OR tonReconnect.Q;

fbTcpConnect(
    Execute     := bEnableConnect, 
    DstAdr      := tmpIpAddress, 
    DstTcpPort  := tmpPort,      
    SrcTcpPort  := 0,
    Socket      => SocketID_Int,
    Done        => bConnectDone,
    Busy        => bConnectBusy,
    Error       => bConnectError,
    ErrorID     => wConnectErrorID
);

IF bConnectDone THEN Connected := TRUE; END_IF;
IF bConnectError THEN Connected := FALSE; END_IF;

// --- 4. MACCHINA A STATI RICEZIONE ---

IF NOT Connected THEN
    iRcvState := 0;
    bExecuteRcv := FALSE;
    iTestState := 0; 
END_IF;

CASE iRcvState OF
    0: // IDLE
        IF Connected AND NOT bRcvBusy AND NOT bRcvError THEN
            bExecuteRcv := TRUE; 
            iRcvState := 10;     
        END_IF;

    10: // WAIT
        IF bRcvDone THEN iRcvState := 20; 
        ELSIF bRcvError THEN iRcvState := 20; END_IF;

    20: // RESET
        bExecuteRcv := FALSE; 
        IF NOT bRcvDone AND NOT bRcvBusy THEN iRcvState := 0; END_IF;
END_CASE;

fbSocketRcv(
    Execute := bExecuteRcv,
    Socket  := SocketID_Int,
    TimeOut := 1,              
    Size    := UINT#512,       
    RcvDat  := RxChunk[0],     
    Done    => bRcvDone,
    Busy    => bRcvBusy,
    Error   => bRcvError,
    ErrorID => wRcvErrorID,
    RcvSize => RxChunkLen
);

rTrigValid(CLK := (iRcvState = 20) AND (RxChunkLen > 0) AND NOT bRcvError);
RxChunkValid := rTrigValid.Q;

// --- 5. GESTIONE PRIORITÀ COMANDI ---

CommandTrigger := FALSE; 

// --- RECUPERO NOME RICETTA ---

sCurrentRecipe := G_Idecon_LastWeight.RecipeName; 
IF sCurrentRecipe = '' THEN sCurrentRecipe := G_Idecon_StatP.RecipeName; END_IF;
IF sCurrentRecipe = '' THEN sCurrentRecipe := '400 g'; END_IF; // Fallback

G_Test_Ejector_State := iTestState; 

// Timeout di sicurezza per sbloccare lo stato 10 se la bilancia non risponde

tonTestTimeout(IN := (iTestState = 10), PT := T#5S);
IF tonTestTimeout.Q THEN
    iTestState := 0; // Abortisci test per timeout
    G_Test_Ejector_Start := FALSE;
END_IF;

CASE iTestState OF
    0: // IDLE
        IF G_Test_Ejector_Start THEN
            // Passo 1: Leggi config
            Command := CONCAT('GETFROMRECIPE=', CONCAT(sCurrentRecipe, '|EJECTOR_1'));
            CommandTrigger := TRUE;
            pollResetSV := TRUE; pollResetP := TRUE;
            tonPollingSTATSV(IN := FALSE); tonPollingSTATP(IN := FALSE);
            iTestState := 10; 
            G_Test_Ejector_Start := FALSE; 
        END_IF;

    10: // WAIT READ (Gestito in Parsing e Timeout)

    15: // READ OK -> DISABILITA
        // Passo 2: Disabilita (Offset=0, Durata=0)
        Command := CONCAT('ALTERRECIPE=', CONCAT(sCurrentRecipe, '|EJECTOR_1|0|0'));
        CommandTrigger := TRUE;
        iTestState := 20; 

    20: // TESTING
        IF G_Test_Ejector_Restore THEN
            // Passo 3: Ripristina
            Command := CONCAT('ALTERRECIPE=', CONCAT(sCurrentRecipe, '|EJECTOR_1|'));
            Command := CONCAT(Command, G_Test_Saved_Offset);
            Command := CONCAT(Command, '|');
            Command := CONCAT(Command, G_Test_Saved_Duration);
            CommandTrigger := TRUE;
            G_Test_Ejector_Restore := FALSE; 
            iTestState := 0; 
        END_IF;
END_CASE;

IF (iTestState = 0) OR (iTestState = 20) THEN 
    
    // A. COMANDO MANUALE
    IF G_Idecon_HMI_Cmd.SendTrigger AND NOT prevHmiSend AND NOT CommandTrigger THEN
        Command := G_Idecon_HMI_Cmd.CmdString;
        CommandTrigger := TRUE;
        pollResetSV := TRUE; pollResetP := TRUE;
        tonPollingSTATSV(IN := FALSE); tonPollingSTATP(IN := FALSE);
        G_Idecon_HMI_Cmd.SendTrigger := FALSE;
    END_IF;
    prevHmiSend := G_Idecon_HMI_Cmd.SendTrigger;

    // B. POLLING
    IF NOT CommandTrigger AND (iTestState = 0) AND NOT G_Idecon_HMI_Cmd.SendTrigger THEN 
        tonPollingSTATSV(IN := (Enable AND Connected AND NOT pollResetSV), PT := T#2S); 
        tonPollingSTATP(IN := (Enable AND Connected AND NOT pollResetP), PT := T#5S);   

        pollResetSV := FALSE; pollResetP := FALSE;

        IF tonPollingSTATSV.Q AND NOT prevPollSVQ THEN
            Command := 'STATSV'; CommandTrigger := TRUE; pollResetSV := TRUE;
        ELSIF tonPollingSTATP.Q AND NOT prevPollPQ THEN
            Command := 'STATREQ'; CommandTrigger := TRUE; pollResetP := TRUE;
        END_IF;
        prevPollSVQ := tonPollingSTATSV.Q; prevPollPQ := tonPollingSTATP.Q;
    END_IF;
END_IF;

// --- 6. CHIAMATA DRIVER ---

Idecon(
    Enable := Enable,
    MsgFilter := MsgFilter,
    RxIn := RxChunk,
    RxInLen := RxChunkLen,
    RxInValid := RxChunkValid, 
    TxConsumed := TxConsumed,
    Command := Command,
    CommandTrigger := CommandTrigger
);

// --- 7. PARSING RISPOSTE ---

newMsg := (Idecon.LastMessage <> prevLastMessage);
prevLastMessage := Idecon.LastMessage;

IF newMsg THEN
    sTempParse := Idecon.LastMessage;
    
    // --- PARSING ROBUSTO PER TEST EIETTORE (CORRETTO) ---
    // Se siamo nello stato di attesa risposta (10)
    IF (iTestState = 10) THEN
        // Controlla se è un messaggio di risposta a GETFROMRECIPE
        IF IDECON_StartsWith(sTempParse, 'GETFROMRECIPE=') THEN
            // Rimuovi prefisso: 'GETFROMRECIPE=' (14 char)
            sTempParse := DELETE(sTempParse, 14, 1); 
            
            // --- FIX ROBUSTEZZA: NON controlliamo il campo 2 ---
            // Prendiamo direttamente i valori nei campi 3 e 4.
            // Se sono validi, avanziamo.
            
            G_Test_Saved_Offset   := IDECON_FieldAt(sTempParse, 3, '|');
            G_Test_Saved_Duration := IDECON_FieldAt(sTempParse, 4, '|');
            
            // Se abbiamo letto qualcosa di valido, procediamo
            IF (G_Test_Saved_Offset <> '') OR (G_Test_Saved_Duration <> '') THEN
                iTestState := 15; // Successo! Vai allo step successivo
            END_IF;
        END_IF;
    END_IF;
    
    // --- PARSING STANDARD ---
    newWeightMsg := IDECON_StartsWith(Idecon.LastMessage, 'WEIGHT=');
    IF newWeightMsg AND NOT prevWeightMsg THEN
        G_ProgressiveID := G_ProgressiveID + 1; 
    END_IF;
    prevWeightMsg := newWeightMsg;
END_IF;

// --- 8. MAPPATURA OUTPUT ---

tmpWeightData := Idecon.Weight;
tmpStatPData  := Idecon.StatP;
G_Idecon_LastSTATSV := Idecon.LastSTATSV;

IF tmpWeightData.Valid THEN G_Idecon_LastWeight := tmpWeightData; G_Idecon_LastWeight.Valid := TRUE; END_IF;
IF tmpStatPData.Valid THEN G_Idecon_StatP := tmpStatPData; G_Idecon_StatP.Valid := TRUE; END_IF;

// --- 9. ERRORI E OPC UA ---

G_System_Error := bConnectError OR bSendError OR bRcvError OR Idecon.Error;

IF G_Idecon_StatP.Valid AND (G_Idecon_StatP.TotalProducts >= G_Idecon_StatP.TotalAccepted) THEN
    totalRejected := G_Idecon_StatP.TotalProducts - G_Idecon_StatP.TotalAccepted;
ELSE totalRejected := 0; END_IF;

// Mapping OPC UA

G_OPCUA_Idecon.Connected := Connected;
G_OPCUA_Idecon.WorkMode := G_Idecon_WorkMode;
G_OPCUA_Idecon.LastSTATSV := G_Idecon_LastSTATSV;
G_OPCUA_Idecon.BatchCode := G_Idecon_BatchCode;
G_OPCUA_Idecon.ProductionOrder := G_Idecon_ProductionOrder;
G_OPCUA_Idecon.Error := G_System_Error;
G_OPCUA_Idecon.ErrorId := UINT_TO_UDINT(WORD_TO_UINT(wConnectErrorID));

G_OPCUA_Idecon.LastWeight.ProgressiveId := G_ProgressiveID;
G_OPCUA_Idecon.LastWeight.TimestampText := G_Idecon_LastWeight.DateTimeText;
G_OPCUA_Idecon.LastWeight.ProductionOrder := G_Idecon_LastWeight.ProductionOrder;
G_OPCUA_Idecon.LastWeight.BatchCode := G_Idecon_LastWeight.BatchCode;
G_OPCUA_Idecon.LastWeight.RecipeName := G_Idecon_LastWeight.RecipeName;
G_OPCUA_Idecon.LastWeight.LineCode := G_Idecon_LastWeight.LineCode;
G_OPCUA_Idecon.LastWeight.SerialNumber := G_Idecon_LastWeight.SerialNumber;
G_OPCUA_Idecon.LastWeight.Weight_g := DINT_TO_LREAL(G_Idecon_LastWeight.WeightMg) / LREAL#1000.0;
G_OPCUA_Idecon.LastWeight.Delta_g := DINT_TO_LREAL(G_Idecon_LastWeight.DeltaToNominalMg) / LREAL#1000.0;
G_OPCUA_Idecon.LastWeight.Classification := G_Idecon_LastWeight.Classification;
// FIX ESPULSIONE: Controllo Bit 8 (Expelled Generico) o Bit 15 (Expelled per Consenso)
// Usiamo la conversione esplicita per evitare errori di sintassi
G_OPCUA_Idecon.LastWeight.Expelled := ((G_Idecon_LastWeight.Classification AND DWORD#16#100) > DWORD#0) OR 
                                      ((G_Idecon_LastWeight.Classification AND DWORD#16#8000) > DWORD#0);
G_OPCUA_Idecon.LastWeight.Valid := G_Idecon_LastWeight.Valid;

G_OPCUA_Idecon.Stats.TotalProducts := G_Idecon_StatP.TotalProducts;
G_OPCUA_Idecon.Stats.TotalAccepted := G_Idecon_StatP.TotalAccepted;
G_OPCUA_Idecon.Stats.TotalRejected := totalRejected;
G_OPCUA_Idecon.Stats.RejectedPlusPlus := G_Idecon_StatP.RejectedPlusPlus;
G_OPCUA_Idecon.Stats.CannotBeWeighed := G_Idecon_StatP.CannotBeWeighed;
G_OPCUA_Idecon.Stats.MetalCategory := G_Idecon_StatP.MetalCategory;
G_OPCUA_Idecon.Stats.Valid := G_Idecon_StatP.Valid;

// --- 10. INVIO SOCKET ---

sendTrigger := (Idecon.TxOutValid AND NOT prevTxOutValid);
prevTxOutValid := Idecon.TxOutValid;

IF sendTrigger THEN TxBuffer := Idecon.TxOut; END_IF;

fbSocketSend(
    Execute := (Enable AND Connected AND sendTrigger),
    Socket := SocketID_Int,
    SendDat := TxBuffer[0], 
    Size := Idecon.TxOutLen,
    Done => bSendDone,
    Busy => bSendBusy,
    Error => bSendError,
    ErrorID => wSendErrorID
);
TxConsumed := bSendDone;

IF NOT Enable AND Connected THEN
    fbClose(Execute := TRUE, Socket := SocketID_Int);
ELSE
    fbClose(Execute := FALSE, Socket := SocketID_Int);
END_IF;