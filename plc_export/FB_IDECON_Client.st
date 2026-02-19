// ============================================================================
// Function Block: FB_IDECON_Client
// Description: Client TCP per comunicazione con bilancia IDECON
// Version: 1.0
// ============================================================================

FUNCTION_BLOCK FB_IDECON_Client
VAR_INPUT
    Execute                 : BOOL;             // Esegui comando
    Command                 : STRING[255];      // Comando da inviare
    Timeout                 : TIME := T#5S;     // Timeout risposta
END_VAR

VAR_OUTPUT
    Done                    : BOOL;             // Comando completato con successo
    Busy                    : BOOL;             // In esecuzione
    Error                   : BOOL;             // Errore
    ErrorID                 : WORD;             // Codice errore (0=nessuno)
    Response                : STRING[512];      // Risposta ricevuta
    ResponseRaw             : ARRAY[0..511] OF BYTE; // Risposta raw bytes
    ResponseLen             : UINT;             // Lunghezza risposta
END_VAR

VAR_IN_OUT
    Socket                  : _sSOCKET;         // Socket TCP
END_VAR

VAR
    // Stato FSM
    State                   : INT := 0;         // Stato macchina
    
    // Timer
    TimeoutTimer            : TON;              // Timer timeout
    RetryTimer              : TON;              // Timer retry
    
    // Buffer
    SendBuffer              : ARRAY[0..511] OF BYTE;
    RecvBuffer              : ARRAY[0..1023] OF BYTE;
    CmdLen                  : UINT;
    RetryCount              : INT := 0;
    MaxRetries              : INT := 3;
    
    // Costanti protocollo
    STX                     : BYTE := BYTE#16#02;  // Start of Text
    ETX                     : BYTE := BYTE#16#03;  // End of Text
    
    // Variabili interne
    i                       : INT;
    j                       : INT;
    StrLen                  : UINT;
    RecvDone                : BOOL;
    SendDone                : BOOL;
    
END_VAR

// Stati FSM
// 0: Idle
// 1: Prepara comando
// 2: Invia STX
// 3: Invia comando
// 4: Invia ETX
// 5: Attendi risposta
// 6: Ricevi dati
// 7: Parsa risposta
// 8: Completato
// 9: Errore

// ============================================================================
// IMPLEMENTAZIONE
// ============================================================================

IF NOT Execute AND State <> 0 THEN
    // Reset su fronte negativo Execute
    State := 0;
    Busy := FALSE;
END_IF;

CASE State OF
    
    0: // Idle
        Done := FALSE;
        Error := FALSE;
        ErrorID := WORD#0;
        Busy := FALSE;
        RetryCount := 0;
        
        IF Execute THEN
            State := 1;
            Busy := TRUE;
        END_IF;
        
    1: // Prepara comando
        // Prepara buffer: STX + Comando + ETX
        StrLen := LEN(Command);
        
        IF StrLen = 0 OR StrLen > 250 THEN
            Error := TRUE;
            ErrorID := WORD#1; // Comando vuoto o troppo lungo
            State := 9;
        ELSE
            // Copia comando in buffer
            FOR i := 0 TO INT#(StrLen - 1) DO
                SendBuffer[i + 1] := STRING_TO_BYTE(MID(Command, 1, UINT#(i + 1)));
            END_FOR;
            
            CmdLen := StrLen;
            State := 2;
        END_IF;
        
    2: // Invia STX
        Socket.Send(ADR(STX), 1);
        
        IF Socket.Done THEN
            State := 3;
        ELSIF Socket.Error THEN
            Error := TRUE;
            ErrorID := Socket.ErrorID;
            State := 9;
        END_IF;
        
    3: // Invia comando
        Socket.Send(ADR(SendBuffer[1]), CmdLen);
        
        IF Socket.Done THEN
            State := 4;
        ELSIF Socket.Error THEN
            Error := TRUE;
            ErrorID := Socket.ErrorID;
            State := 9;
        END_IF;
        
    4: // Invia ETX
        Socket.Send(ADR(ETX), 1);
        
        IF Socket.Done THEN
            State := 5;
            TimeoutTimer(IN := TRUE, PT := Timeout);
        ELSIF Socket.Error THEN
            Error := TRUE;
            ErrorID := Socket.ErrorID;
            State := 9;
        END_IF;
        
    5: // Attendi risposta
        TimeoutTimer(IN := TRUE);
        
        IF TimeoutTimer.Q THEN
            // Timeout - retry?
            IF RetryCount < MaxRetries THEN
                RetryCount := RetryCount + 1;
                State := 1; // Riprova
                TimeoutTimer(IN := FALSE);
            ELSE
                Error := TRUE;
                ErrorID := WORD#16#8001; // Timeout
                State := 9;
            END_IF;
        END_IF;
        
        // Controlla se ci sono dati
        IF Socket.Available > 0 THEN
            State := 6;
            TimeoutTimer(IN := FALSE);
        END_IF;
        
    6: // Ricevi dati
        Socket.Recv(ADR(RecvBuffer), SIZEOF(RecvBuffer), RecvLen);
        
        IF Socket.Done THEN
            State := 7;
        ELSIF Socket.Error THEN
            Error := TRUE;
            ErrorID := Socket.ErrorID;
            State := 9;
        END_IF;
        
    7: // Parsa risposta
        // Rimuovi STX e ETX se presenti
        IF RecvLen > 0 THEN
            j := 0;
            FOR i := 0 TO INT#(RecvLen - 1) DO
                // Salta STX iniziale
                IF i = 0 AND RecvBuffer[i] = STX THEN
                    CONTINUE;
                END_IF;
                // Salta ETX finale
                IF i = INT#(RecvLen - 1) AND RecvBuffer[i] = ETX THEN
                    CONTINUE;
                END_IF;
                // Copia byte valido
                ResponseRaw[j] := RecvBuffer[i];
                j := j + 1;
            END_FOR;
            
            // Converti in stringa
            Response := '';
            FOR i := 0 TO j - 1 DO
                IF ResponseRaw[i] >= BYTE#32 AND ResponseRaw[i] <= BYTE#126 THEN
                    Response := CONCAT(Response, BYTE_TO_STRING(ResponseRaw[i]));
                END_IF;
            END_FOR;
            
            ResponseLen := UINT#(j);
        END_IF;
        
        State := 8;
        
    8: // Completato
        Done := TRUE;
        Busy := FALSE;
        Error := FALSE;
        
        IF NOT Execute THEN
            State := 0;
        END_IF;
        
    9: // Errore
        Error := TRUE;
        Busy := FALSE;
        Done := FALSE;
        
        IF NOT Execute THEN
            State := 0;
        END_IF;
        
END_CASE;

END_FUNCTION_BLOCK