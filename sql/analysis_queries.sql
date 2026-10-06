-- A: executive category contribution and target gaps. Currency AUD, synthetic.
SELECT Category,Revenue,RevenueYoY,GrossMargin,Contribution,
       Revenue-TargetRevenue RevenueVsTarget,SimulatedMarketShare
FROM category_performance WHERE Year=2024 ORDER BY Revenue DESC;

-- A: opportunity candidates. Velocity is units per active SKU-store-day.
WITH candidates AS (
 SELECT *,Revenue*(0.70-Distribution)/NULLIF(Distribution,0) IndicativeDistributionRevenue
 FROM sku_productivity WHERE Year=2024 AND Distribution<0.70 AND GrossMargin>0.35
)
SELECT *,DENSE_RANK() OVER(ORDER BY IndicativeDistributionRevenue DESC) OpportunityRank
FROM candidates ORDER BY OpportunityRank;

-- A: volume growth that dilutes contribution; ranking supports campaign triage.
SELECT CampaignKey,Product,Channel,Lift,ROI,NetIncrementalProfit,
 ROW_NUMBER() OVER(ORDER BY NetIncrementalProfit) ReviewOrder
FROM promotion_evaluation WHERE Year=2024 AND Lift>0 AND NetIncrementalProfit<0
ORDER BY ReviewOrder LIMIT 15;

-- A: exact additive change bridge. PriceMix includes realised discount/pack effects.
SELECT SUM(RevenueDelta) RevenueDelta,SUM(VolumeEffect) VolumeEffect,
 SUM(PriceMixEffect) PriceMixEffect,SUM(InteractionEffect) InteractionEffect,
 SUM(NewProductEffect) NewProductEffect FROM revenue_bridge;

-- A: customer-level trailing 28 calendar days (not 28 transaction rows).
WITH daily AS (SELECT Date,CustomerKey,SUM(Revenue) Revenue FROM fmcg_FactSales GROUP BY Date,CustomerKey)
SELECT Date,CustomerKey,Revenue,
 SUM(Revenue) OVER(PARTITION BY CustomerKey ORDER BY julianday(Date) RANGE BETWEEN 27 PRECEDING AND CURRENT ROW) Rolling28DayRevenue
FROM daily ORDER BY CustomerKey,Date;

-- B: which constructors convert their grids into GP points?
SELECT Season,Constructor,COUNT(*) Starts,SUM(Points) GPPoints,
 SUM(Points-GridPointsBenchmark) GPPointsAboveGridBenchmark,
 AVG(PositionGain) AvgClassifiedPositionGain,AVG(NonFinish) NonFinishRate
FROM f1_execution GROUP BY Season,Constructor ORDER BY Season,GPPoints DESC;

-- B: movement and sample size; pit-lane starts and nonfinishers excluded.
SELECT Driver,Starts,EligibleMovementStarts,AvgClassifiedPositionGain,NonFinishes
FROM driver_intelligence WHERE Season=2024 AND EligibleMovementStarts>=10
ORDER BY AvgClassifiedPositionGain DESC;

-- B: location-specific execution; no causal overtaking claim.
SELECT Circuit,COUNT(*) Starts,AVG(PositionGain) ClassifiedPositionMovement,AVG(NonFinish) NonFinishRate
FROM f1_execution GROUP BY Circuit HAVING COUNT(*)>=30 ORDER BY NonFinishRate DESC;

-- B: teammate-normalized comparison for shared classified race entries.
SELECT *,1.0*AheadFinishes/ComparableStarts AheadFinishRate
FROM teammate_comparison WHERE Season=2024 AND ComparableStarts>=10 ORDER BY AheadFinishRate DESC;

-- B: compare pit durations only within a race to reduce circuit-length effects.
WITH contextual AS (
 SELECT p.RaceKey,p.ConstructorKey,p.DurationSeconds,
 p.DurationSeconds-AVG(p.DurationSeconds) OVER(PARTITION BY RaceKey) SecondsVsRaceMean
 FROM f1_FactPitStops p WHERE TimingEligible=1
)
SELECT c.Constructor,COUNT(*) EligibleStops,AVG(SecondsVsRaceMean) MeanSecondsVsRaceMean
FROM contextual x JOIN f1_DimConstructor c USING(ConstructorKey)
GROUP BY c.Constructor ORDER BY MeanSecondsVsRaceMean;
