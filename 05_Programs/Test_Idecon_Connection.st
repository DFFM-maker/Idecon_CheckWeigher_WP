// ==============================================================================
// TEST: Idecon_ConnectionTest
// DESCRIZIONE: Test di connessione alla pesatrice IDECON
// IP: 172.16.224.210 | Port: 50000
// ==============================================================================

VAR
    // TCP Connection
    fbTcpConnect : SysSocketConnect;
    fbSocketRcv : SysSocketRcv;
    fbSocketSend : SysSocketSend;
    fbClose : SysSocketClose;
    
    // Status
    SocketID : UDINT;
    Connected : BOOL;
    bConnectBusy : BOOL;
    bConnectDone : BOOL;
    bConnectError : BOOL;
    wConnectErrorID : WORD;
    bRcvDone : BOOL;
    bRcvBusy : BOOL;
    bRcvError : BOOL;
    wRcvErrorID : WORD;
    bSendDone : BOOL;
    bSendBusy : BOOL;
    bSendError : BOOL;
    wSendErrorID : WORD;
    
    // RX/TX Buffers
    RxBuf : ARRAY[0..511] OF BYTE;
    RxLen : UINT;
    TxBuf : ARRAY[0..255] OF BYTE;
    TxLen : UINT;
    
    // Test Control
    TestEnable : BOOL;
    TestStep : INT;
    tonReceive : TON;
    tonConnect : TON;
    ResultMessage : STRING[255];
    ConnectionStatus : STRING[50];
    
    // Received Data
    ReceivedString : STRING[512];
    ResponseCount : UDINT;
END_VAR

// ==============================================================================
// MAIN TEST LOGIC
// ==============================================================================

IF NOT TestEnable THEN
    // Reset
    Connected := FALSE;
    TestStep := 0;
    ResponseCount := 0;
    ReceivedString := '';
    ConnectionStatus := 'Idle';
    ResultMessage := '';
    
    fbTcpConnect(Execute := FALSE);
    fbSocketRcv(Execute := FALSE);
    fbSocketSend(Execute := FALSE);
    fbClose(Execute := FALSE);
    
    RETURN;
END_IF;

// Connection Timeout (10 seconds)
tonConnect(IN := TestEnable, PT := T#10S);
IF tonConnect.Q THEN
    ConnectionStatus := 'Timeout - No Connection';
    TestStep := 100; // Error state
END_IF;

// Receive Timeout (3 seconds per command)
tonReceive(IN := (TestStep = 20), PT := T#3S);
IF tonReceive.Q THEN
    ConnectionStatus := 'Timeout - No Response';
    TestStep := 100;
END_IF;

// State Machine
CASE TestStep OF
    0: // Connect
        ConnectionStatus := 'Connecting...';
        fbTcpConnect(
            Execute := TRUE,
            DstAdr := '172.16.224.210',
            DstTcpPort := 50000,
            SrcTcpPort := 0,
            Socket => SocketID,
            Done => bConnectDone,
            Busy => bConnectBusy,
            Error => bConnectError,
            ErrorID => wConnectErrorID
        );
        
        IF bConnectDone THEN
            Connected := TRUE;
            TestStep := 10;
            ConnectionStatus := 'Connected!';
        ELSIF bConnectError THEN
            ConnectionStatus := CONCAT('Connect Error: ', UINT_TO_STRING(wConnectErrorID));
            TestStep := 100;
        END_IF;
        
    10: // Start Receiving
        fbTcpConnect(Execute := FALSE);
        ConnectionStatus := 'Waiting for data...';
        TestStep := 20;
        
    20: // Receive Loop
        fbSocketRcv(
            Execute := TRUE,
            Socket := SocketID,
            TimeOut := 1,
            Size := 512,
            RcvDat => RxBuf[0],
            Done => bRcvDone,
            Busy => bRcvBusy,
            Error => bRcvError,
            ErrorID => wRcvErrorID,
            RcvSize => RxLen
        );
        
        IF bRcvDone AND RxLen > 0 THEN
            // Process received data
            fbSocketRcv(Execute := FALSE);
            
            // Convert bytes to string for display
            ReceivedString := '';
            FOR i := 0 TO INT_TO_UINT(RxLen - 1) DO
                IF RxBuf[i] >= 32 AND RxBuf[i] <= 126 THEN
                    ReceivedString := CONCAT(ReceivedString, BYTE_TO_CHAR(RxBuf[i]));
                ELSE
                    ReceivedString := CONCAT(ReceivedString, '.');
                END_IF;
            END_FOR;
            
            ResponseCount := ResponseCount + 1;
            ConnectionStatus := CONCAT('Data Received (', UINT_TO_STRING(ResponseCount), ')');
            
            // Send STATSV command to test
            TestStep := 30;
        ELSIF bRcvError THEN
            ConnectionStatus := 'Receive Error';
            TestStep := 100;
        END_IF;
        
    30: // Send STATSV Command
        // Prepare STATSV command: STX + 'STATSV' + ETX
        TxBuf[0] := 16#02;  // STX
        TxBuf[1] := 16#53;  // S
        TxBuf[2] := 16#54;  // T
        TxBuf[3] := 16#41;  // A
        TxBuf[4] := 16#54;  // T
        TxBuf[5] := 16#53;  // S
        TxBuf[6] := 16#56;  // V
        TxBuf[7] := 16#03;  // ETX
        TxLen := 8;
        
        fbSocketSend(
            Execute := TRUE,
            Socket := SocketID,
            SendDat => TxBuf[0],
            Size := TxLen,
            Done => bSendDone,
            Busy => bSendBusy,
            Error => bSendError,
            ErrorID => wSendErrorID
        );
        
        IF bSendDone THEN
            ResultMessage := 'STATSV Command Sent';
            TestStep := 20; // Back to receive
        ELSIF bSendError THEN
            ConnectionStatus := 'Send Error';
            TestStep := 100;
        END_IF;
        
    100: // Error / Cleanup
        ResultMessage := 'Test Ended with Error';
        
    200: // Disconnect
        fbClose(Execute := TRUE, Socket := SocketID);
        IF fbClose.Done THEN
            Connected := FALSE;
            TestEnable := FALSE;
            ConnectionStatus := 'Disconnected';
        END_IF;
END_CASE;

// Auto-stop after 30 seconds of successful connection
IF TestStep = 20 AND TestEnable THEN
    // Keep receiving...
END_IF;