// ============================================================================
// DataType: IdeconInterface
// Description: Struttura principale unificata per gestione bilancia IDECON
//              Unica variabile in Global Variables: G_Idecon : IdeconInterface
// Version: 1.0
// ============================================================================

TYPE IdeconInterface :
STRUCT
    // === CONFIGURAZIONE (inizializzata in HSM_SpecificationsSetting) ========
    // Esempio: G_Idecon.Config.IpAddress := '172.16.224.210';
    Config                  : Idecon_Config;
    
    // === SOCKET TCP (gestito da FB_IDECON_Client) ===========================
    // Non modificare direttamente, usare FB
    Socket                  : _sSOCKET;
    
    // === STATO COMUNICAZIONE =================================================
    // Monitoraggio stato connessione e online/offline
    Comm                    : Idecon_CommStatus;
    
    // === DATI RICEVUTI DALLA BILANCIA ========================================
    // Ultimi dati aggiornati automaticamente
    LastWeight              : Idecon_WeightData;    // Ultima pesata WEIGHT
    BatchStats              : Idecon_BatchStats;    // Statistiche STATP
    Status                  : Idecon_Status;        // Stato macchina STATSV
    LastEvent               : Idecon_EventData;     // Ultimo evento EVENT
    
    // === COMANDO ATTIVO ======================================================
    // Per inviare comandi alla bilancia
    Cmd                     : Idecon_Command;
    
    // === STATISTICHE LOCALI PLC ==============================================
    // Contatori e calcoli fatti dal PLC
    Stats                   : Idecon_LocalStats;
    
    // === FLAG ERRORE SISTEMA =================================================
    // TRUE quando c'è errore grave comunicazione
    SystemError             : BOOL;
    
    // === VERSIONE E DIAGNOSTICA ==============================================
    Version                 : UINT := 100;          // Versione struct (1.00)
    
END_STRUCT;
END_TYPE