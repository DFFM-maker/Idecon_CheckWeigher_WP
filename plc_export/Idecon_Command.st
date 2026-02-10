// ============================================================================
// DataType: Idecon_Command
// Description: Struttura per gestione comando singolo verso bilancia
// ============================================================================

TYPE Idecon_Command :
STRUCT
    // === Input (da programma chiamante) ======================================
    Execute                 : BOOL;             // Esegui comando (fronte salita)
    Command                 : STRING[255];      // Stringa comando (es. "STATSV")
    Timeout                 : TIME := T#5S;     // Timeout attesa risposta
    
    // === Output (da FB_IDECON_Client) ========================================
    Done                    : BOOL;             // Comando completato con successo
    Busy                    : BOOL;             // Comando in esecuzione
    Error                   : BOOL;             // Errore durante esecuzione
    ErrorID                 : WORD;             // Codice errore specifico
    
    // === Risposta ============================================================
    Response                : STRING[512];      // Risposta testuale da bilancia
    ResponseRaw             : ARRAY[0..511] OF BYTE;  // Risposta come array byte
    ResponseLen             : UINT;             // Lunghezza risposta in bytes
    ResponseTime_ms         : UDINT;            // Tempo risposta (ms)
    
    // === Timestamp ===========================================================
    ExecuteTime             : LINT;             // Quando è stato eseguito
    DoneTime                : LINT;             // Quando è stato completato
    
END_STRUCT;
END_TYPE