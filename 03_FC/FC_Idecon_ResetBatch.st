// ==============================================================================
// FUNZIONE: FC_Idecon_ResetBatch
// DESCRIZIONE: Resetta statistiche batch su cambio lotto
// INPUT: CurrentBatchCode (STRING[64]) - Codice lotto corrente
// OUTPUT: BatchResetDone (BOOL) - TRUE se reset eseguito
// NOTE: Implementare nel task ciclico monitorando cambio G_Idecon_BatchCode
// ==============================================================================

VAR_INPUT
    CurrentBatchCode : STRING[64];
END_VAR

VAR_OUTPUT
    BatchResetDone : BOOL;
END_VAR

VAR
    PreviousBatchCode : STRING[64];
    CurrentTimestamp_Unix_ms : LINT;
END_VAR

// Get current timestamp (requires SysTicks function or PLC time)
// CurrentTimestamp_Unix_ms := ...;  // Da implementare con funzione di sistema

// Detect batch code change
IF CurrentBatchCode <> PreviousBatchCode THEN
    // Reset all statistics
    G_Idecon_BatchStats.BatchStartTime_Unix := CurrentTimestamp_Unix_ms;
    G_Idecon_BatchStats.BatchDuration_Sec := 0;
    G_Idecon_BatchStats.TotalProducts := 0;
    G_Idecon_BatchStats.AcceptedProducts := 0;
    G_Idecon_BatchStats.RejectedUnderweight := 0;
    G_Idecon_BatchStats.RejectedOverweight := 0;
    G_Idecon_BatchStats.MissingProducts := 0;
    G_Idecon_BatchStats.TotalWeight_kg := 0.0;
    G_Idecon_BatchStats.AverageWeight_g := 0.0;
    G_Idecon_BatchStats.MinWeightMeasured_g := 999999.0;
    G_Idecon_BatchStats.MaxWeightMeasured_g := 0.0;
    G_Idecon_BatchStats.StdDeviation_g := 0.0;
    G_Idecon_BatchStats.YieldPercentage := 0.0;
    G_Idecon_BatchStats.RejectionRate := 0.0;
    G_Idecon_BatchStats.ProductionRate_PPM := 0.0;
    G_Idecon_BatchStats.BatchActive := TRUE;
    G_Idecon_BatchStats.DataValid := FALSE;
    
    // Save previous batch code
    PreviousBatchCode := CurrentBatchCode;
    
    BatchResetDone := TRUE;
ELSE
    BatchResetDone := FALSE;
END_IF;

// Update duration if batch is active
IF G_Idecon_BatchStats.BatchActive AND CurrentTimestamp_Unix_ms > 0 THEN
    G_Idecon_BatchStats.BatchDuration_Sec := (CurrentTimestamp_Unix_ms - G_Idecon_BatchStats.BatchStartTime_Unix) / 1000;
END_IF;