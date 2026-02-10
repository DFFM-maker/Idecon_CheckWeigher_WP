// ============================================================================
// DataType: Idecon_CommStatus
// Description: Stato comunicazione TCP con bilancia IDECON
// ============================================================================

TYPE Idecon_CommStatus :
STRUCT
    // === Stato Connessione ===================================================
    Connected               : BOOL;             // Socket connesso fisicamente
    Online                  : BOOL;             // Comunicazione attiva (ultimo msg < timeout)
    Ready                   : BOOL;             // Pronto per inviare comandi
    
    // === Statistiche Comunicazione ===========================================
    RxCount                 : UDINT;            // Totale messaggi ricevuti
    TxCount                 : UDINT;            // Totale comandi inviati
    ErrorCount              : UDINT;            // Contatore errori
    RetryCount              : UINT;             // Retry in corso
    
    // === Timestamp ===========================================================
    LastRxTime              : LINT;             // Timestamp ultimo messaggio ricevuto (Unix ms)
    LastTxTime              : LINT;             // Timestamp ultimo comando inviato
    ConnectionTime          : LINT;             // Timestamp connessione stabilita
    
    // === Errori ==============================================================
    LastError               : WORD;             // Codice ultimo errore
    LastErrorTime           : LINT;             // Timestamp ultimo errore
    
    // === Stato Dettagliato ===================================================
    StatusCode              : STRING[8];        // Ultimo STATSV ricevuto
    WorkMode                : UINT;             // 1=LOCAL, 2=REMOTE, 3=MAINTENANCE
    IsLocalMode             : BOOL;             // TRUE se in LOCAL
    IsRemoteMode            : BOOL;             // TRUE se in REMOTE
    
END_STRUCT;
END_TYPE