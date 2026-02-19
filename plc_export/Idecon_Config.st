// ============================================================================
// DataType: Ideon_Config
// Description: Configurazione rete e parametri bilancia IDECON
// ============================================================================

TYPE Idecon_Config :
STRUCT
    // === Parametri Rete ======================================================
    IpAddress               : STRING[15] := '172.16.224.210';  // IP bilancia
    TcpPort                 : UINT := 50000;                    // Porta TCP
    
    // === Timeout (millisecondi) ==============================================
    ConnectionTimeout_ms    : UDINT := 10000;                   // Timeout connessione
    CommandTimeout_ms       : UDINT := 5000;                    // Timeout comando
    ResponseTimeout_ms      : UDINT := 5000;                    // Timeout risposta
    
    // === Polling =============================================================
    PollInterval_ms         : UDINT := 5000;                    // Intervallo polling STATSV
    
    // === Retry ===============================================================
    MaxRetries              : UINT := 3;                        // Numero max retry
    
    // === MSGFILTER ===========================================================
    MsgFilterValue          : UINT := 23;                       // 0b10111 = risp+err+ev+pesi
    
    // === Statistiche =========================================================
    StatsCadency_sec        : UINT := 30;                       // Frequenza STATP (secondi)
    
    // === Abilitazione ========================================================
    Connect                 : BOOL := FALSE;                    // Abilita connessione
    AutoReconnect           : BOOL := TRUE;                     // Riconnessione automatica
    
END_STRUCT;
END_TYPE