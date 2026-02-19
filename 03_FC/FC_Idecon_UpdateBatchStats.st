// ==============================================================================
// FUNZIONE: FC_Idecon_UpdateBatchStats
// DESCRIZIONE: Aggiorna statistiche batch su ogni pesata ricevuta da IDECON
// NOTE: Chiamare nel task ciclico quando G_Idecon_LastWeight.Valid = TRUE
// ==============================================================================

// Increment total counter
G_Idecon_BatchStats.TotalProducts := G_Idecon_BatchStats.TotalProducts + 1;

// Classify based on weight limits
IF G_Idecon_LastWeight.Weight_g >= G_Idecon_BatchConfig.MinWeight_g AND 
   G_Idecon_LastWeight.Weight_g <= G_Idecon_BatchConfig.MaxWeight_g THEN
    G_Idecon_BatchStats.AcceptedProducts := G_Idecon_BatchStats.AcceptedProducts + 1;
ELSIF G_Idecon_LastWeight.Weight_g < G_Idecon_BatchConfig.MinWeight_g THEN
    G_Idecon_BatchStats.RejectedUnderweight := G_Idecon_BatchStats.RejectedUnderweight + 1;
ELSE
    G_Idecon_BatchStats.RejectedOverweight := G_Idecon_BatchStats.RejectedOverweight + 1;
END_IF;

// Update weight statistics
G_Idecon_BatchStats.TotalWeight_kg := G_Idecon_BatchStats.TotalWeight_kg + (G_Idecon_LastWeight.Weight_g / 1000.0);

// Update average weight
IF G_Idecon_BatchStats.TotalProducts > 0 THEN
    G_Idecon_BatchStats.AverageWeight_g := (G_Idecon_BatchStats.TotalWeight_kg * 1000.0) / TO_REAL(G_Idecon_BatchStats.TotalProducts);
END_IF;

// Update min/max measured
IF G_Idecon_LastWeight.Weight_g < G_Idecon_BatchStats.MinWeightMeasured_g OR 
   G_Idecon_BatchStats.TotalProducts = 1 THEN
    G_Idecon_BatchStats.MinWeightMeasured_g := G_Idecon_LastWeight.Weight_g;
END_IF;

IF G_Idecon_LastWeight.Weight_g > G_Idecon_BatchStats.MaxWeightMeasured_g THEN
    G_Idecon_BatchStats.MaxWeightMeasured_g := G_Idecon_LastWeight.Weight_g;
END_IF;

// Calculate KPIs
IF G_Idecon_BatchStats.TotalProducts > 0 THEN
    G_Idecon_BatchStats.YieldPercentage := (TO_REAL(G_Idecon_BatchStats.AcceptedProducts) / 
                                           TO_REAL(G_Idecon_BatchStats.TotalProducts)) * 100.0;
    G_Idecon_BatchStats.RejectionRate := (TO_REAL(G_Idecon_BatchStats.RejectedUnderweight + 
                                                   G_Idecon_BatchStats.RejectedOverweight) / 
                                           TO_REAL(G_Idecon_BatchStats.TotalProducts)) * 100.0;
END_IF;

// Calculate production rate (pieces per minute)
IF G_Idecon_BatchStats.BatchDuration_Sec > 0 THEN
    G_Idecon_BatchStats.ProductionRate_PPM := TO_REAL(G_Idecon_BatchStats.TotalProducts) / 
                                               (TO_REAL(G_Idecon_BatchStats.BatchDuration_Sec) / 60.0);
END_IF;

// Set data valid flag after first product
IF G_Idecon_BatchStats.TotalProducts >= 1 THEN
    G_Idecon_BatchStats.DataValid := TRUE;
END_IF;