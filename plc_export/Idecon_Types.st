// ============================================================================
// DataType: Idecon_Status
// Description: Stato macchina da risposta STATSV
// Version: 1.0
// ============================================================================

TYPE Idecon_Status :
STRUCT
    // === Codice Stato (8 caratteri) ==========================================
    StatusCode              : STRING[8];        // Codice completo (es. "20110011")
    
    // === Posizione 1: Stato Motori ==========================================
    MotorStatus             : UINT;             // 0=Fermo, 1=Regolazione, 2=Pronto, 3=Standby, 4=Ripresa
    MotorRunning            : BOOL;             // TRUE se in moto
    
    // === Posizione 2: Produzione =============================================
    ProductionStarted       : BOOL;             // 1=Produzione attiva
    
    // === Posizione 3-5: Allarmi ==============================================
    HasErrors               : BOOL;             // 1=Errori presenti
    HasWarnings             : BOOL;             // 1=Warning presenti
    HasMessages             : BOOL;             // 1=Messaggi presenti
    
    // === Posizione 6: Statistiche ============================================
    StatsEnabled            : BOOL;             // 1=Invio STATP abilitato
    
    // === Posizione 7: Modalità Operativa =====================================
    WorkMode                : UINT;             // 1=LOCAL, 2=REMOTE, 3=MAINTENANCE
    IsLocalMode             : BOOL;             // TRUE se in LOCAL
    IsRemoteMode            : BOOL;             // TRUE se in REMOTE
    IsMaintenanceMode       : BOOL;             // TRUE se in MAINTENANCE
    
    // === Posizione 8: Connessione ============================================
    ConnectionStatus        : UINT;             // Stato connessione
    
    // === Timestamp ===========================================================
    ReceivedTime            : LINT;             // Timestamp ricezione
    Valid                   : BOOL;             // Dati validi
    
END_STRUCT;
END_TYPE

// ============================================================================
// DataType: Idecon_EventData
// Description: Dati evento da messaggio EVENT
// Version: 1.0
// ============================================================================

TYPE Idecon_EventData :
STRUCT
    Timestamp               : STRING[32];       // Data/ora evento
    ProductionOrder         : STRING[64];       // Ordine
    BatchCode               : STRING[64];       // Batch
    RecipeName              : STRING[32];       // Ricetta
    LineCode                : STRING[32];       // Linea
    SerialNumber            : STRING[16];       // Serial
    
    EventCode               : UINT;             // Codice evento (1000-9999)
    EventDescription        : STRING[255];      // Descrizione testuale
    Operator                : STRING[32];       // Operatore
    
    // Flag comuni
    IsError                 : BOOL;             // TRUE se errore
    IsWarning               : BOOL;             // TRUE se warning
    IsInfo                  : BOOL;             // TRUE se informativo
    
    // Timestamp
    ReceivedTime            : LINT;
    Valid                   : BOOL;
    
END_STRUCT;
END_TYPE

// ============================================================================
// DataType: Idecon_Config
// Description: Configurazione connessione IDECON
// Version: 1.0
// ============================================================================

TYPE Idecon_Config :
STRUCT
    // === Parametri Rete ======================================================
    IpAddress               : STRING[15];       // IP bilancia (es. "172.16.224.210")
    TcpPort                 : UINT;             // Porta (default 50000)
    
    // === Timeout =============================================================
    ConnectionTimeout_ms    : UDINT;            // Timeout connessione (ms)
    CommandTimeout_ms       : UDINT;            // Timeout comando (ms)
    ResponseTimeout_ms      : UDINT;            // Timeout risposta (ms)
    
    // === Polling =============================================================
    PollInterval_ms         : UDINT;            // Intervallo polling STATSV (ms)
    
    // === Retry ===============================================================
    MaxRetries              : UINT;             // Numero massimo retry
    
    // === MSGFILTER ===========================================================
    MsgFilterValue          : UINT;             // Valore MSGFILTER (default 23)
    
    // === Statistiche =========================================================
    StatsCadency_sec        : UINT;             // Frequenza STATP (default 30s)
    
    // === Abilitazione ========================================================
    Connect                 : BOOL;             // Abilita connessione
    AutoReconnect           : BOOL;             // Riconnessione automatica
    
END_STRUCT;
END_TYPE