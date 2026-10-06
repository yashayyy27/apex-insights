-- Facts remain separate. These views enrich one fact at a time, avoiding fanout.
CREATE VIEW commercial_sales AS
SELECT s.*, d.Year, d.YearMonth, p.Product, p.Brand, p.PackMl,
       cat.Category, ch.Channel, r.Region, c.Customer
FROM fmcg_FactSales s
JOIN fmcg_DimDate d ON s.Date=d.Date
JOIN fmcg_DimProduct p ON s.ProductKey=p.ProductKey
JOIN fmcg_DimCategory cat ON s.CategoryKey=cat.CategoryKey
JOIN fmcg_DimChannel ch ON s.ChannelKey=ch.ChannelKey
JOIN fmcg_DimRegion r ON s.RegionKey=r.RegionKey
JOIN fmcg_DimCustomer c ON s.CustomerKey=c.CustomerKey;

CREATE VIEW category_performance AS
WITH sales AS (
 SELECT Year, CategoryKey, Category, SUM(Revenue) Revenue, SUM(Units) Units,
        SUM(VolumeLitres) VolumeLitres, SUM(GrossProfit) GrossProfit
 FROM commercial_sales GROUP BY Year, CategoryKey, Category
), target AS (
 SELECT d.Year, t.CategoryKey, SUM(TargetRevenue) TargetRevenue
 FROM fmcg_FactTargets t JOIN fmcg_DimDate d ON t.Date=d.Date
 GROUP BY d.Year,t.CategoryKey
), market AS (
 SELECT d.Year, m.CategoryKey, SUM(MarketRevenue) MarketRevenue
 FROM fmcg_FactMarket m JOIN fmcg_DimDate d ON m.Date=d.Date
 GROUP BY d.Year,m.CategoryKey
), period AS (
 SELECT s.*, t.TargetRevenue, m.MarketRevenue,
        1.0*s.GrossProfit/NULLIF(s.Revenue,0) GrossMargin,
        1.0*s.Revenue/NULLIF(m.MarketRevenue,0) SimulatedMarketShare,
        1.0*s.Revenue/NULLIF(t.TargetRevenue,0) TargetAttainment,
        1.0*s.Revenue/SUM(s.Revenue) OVER(PARTITION BY s.Year) Contribution
 FROM sales s JOIN target t USING(Year,CategoryKey) JOIN market m USING(Year,CategoryKey)
)
SELECT *, Revenue-LAG(Revenue) OVER(PARTITION BY CategoryKey ORDER BY Year) RevenueDelta,
 Revenue/NULLIF(LAG(Revenue) OVER(PARTITION BY CategoryKey ORDER BY Year),0)-1 RevenueYoY,
 VolumeLitres/NULLIF(LAG(VolumeLitres) OVER(PARTITION BY CategoryKey ORDER BY Year),0)-1 VolumeYoY,
 'SYNTHETIC_DERIVED' DataClass
FROM period;

CREATE VIEW channel_performance AS
WITH s AS (
 SELECT Year,ChannelKey,Channel,RegionKey,Region,SUM(Revenue) Revenue,SUM(Units) Units,SUM(GrossProfit) GrossProfit
 FROM commercial_sales GROUP BY Year,ChannelKey,Channel,RegionKey,Region
), d AS (
 SELECT dt.Year,x.ChannelKey,x.RegionKey,SUM(ActiveStoreDays) ActiveStoreDays,SUM(EligibleStoreDays) EligibleStoreDays
 FROM fmcg_FactDistribution x JOIN fmcg_DimDate dt ON x.Date=dt.Date
 GROUP BY dt.Year,x.ChannelKey,x.RegionKey
)
SELECT s.*,1.0*GrossProfit/Revenue GrossMargin,1.0*Units/ActiveStoreDays Velocity,
 1.0*ActiveStoreDays/EligibleStoreDays Distribution, Revenue/ActiveStoreDays RevenuePerActiveStoreDay,
 Revenue/NULLIF(LAG(Revenue) OVER(PARTITION BY s.ChannelKey,s.RegionKey ORDER BY s.Year),0)-1 RevenueYoY,
 'SYNTHETIC_DERIVED' DataClass
FROM s JOIN d USING(Year,ChannelKey,RegionKey);

CREATE VIEW sku_productivity AS
WITH s AS (
 SELECT Year,ProductKey,Product,Brand,Category,SUM(Revenue) Revenue,SUM(Units) Units,SUM(GrossProfit) GrossProfit
 FROM commercial_sales GROUP BY Year,ProductKey,Product,Brand,Category
), d AS (
 SELECT dt.Year,x.ProductKey,SUM(ActiveStoreDays) ActiveStoreDays,SUM(EligibleStoreDays) EligibleStoreDays
 FROM fmcg_FactDistribution x JOIN fmcg_DimDate dt ON x.Date=dt.Date GROUP BY dt.Year,x.ProductKey
), metrics AS (
 SELECT s.*,d.ActiveStoreDays,d.EligibleStoreDays,1.0*GrossProfit/Revenue GrossMargin,1.0*Units/ActiveStoreDays Velocity,
 1.0*ActiveStoreDays/EligibleStoreDays Distribution FROM s JOIN d USING(Year,ProductKey)
), ranked AS (
 SELECT *,AVG(Velocity) OVER(PARTITION BY Year,Category) CategoryMeanVelocity,
 SUM(GrossProfit) OVER(PARTITION BY Year,Category)/SUM(Revenue) OVER(PARTITION BY Year,Category) CategoryMargin,
 DENSE_RANK() OVER(PARTITION BY Year ORDER BY Revenue DESC) RevenueRank
 FROM metrics
)
SELECT *, CASE WHEN Velocity>=CategoryMeanVelocity AND GrossMargin>=CategoryMargin THEN 'Scale'
 WHEN Velocity>=CategoryMeanVelocity THEN 'Protect margin'
 WHEN GrossMargin>=CategoryMargin THEN 'Test distribution' ELSE 'Review role' END CommercialSegment,
 'SYNTHETIC_DERIVED' DataClass FROM ranked;

CREATE VIEW promotion_evaluation AS
SELECT p.CampaignKey,p.ProductKey,d.Year,prod.Product,cat.Category,ch.Channel,
 MIN(p.Date) StartDate,MAX(p.Date) EndDate,SUM(ActualUnits) ActualUnits,SUM(BaselineUnits) BaselineUnits,
 SUM(IncrementalUnits) IncrementalUnits,SUM(ActualRevenue) ActualRevenue,SUM(BaselineRevenue) BaselineRevenue,
 SUM(ActualGP) ActualGP,SUM(BaselineGP) BaselineGP,SUM(TradeSpend) TradeSpend,
 SUM(NetIncrementalProfit) NetIncrementalProfit,
 1.0*SUM(IncrementalUnits)/SUM(BaselineUnits) Lift,
 1.0*SUM(NetIncrementalProfit)/NULLIF(SUM(TradeSpend),0) ROI,
 SUM(DiscountDepth*ActualUnits)/SUM(ActualUnits) WeightedDiscountDepth,
 CASE WHEN SUM(NetIncrementalProfit)>0 THEN 'Creates simulated value' ELSE 'Dilutes simulated value' END Outcome,
 'SYNTHETIC_DERIVED' DataClass
FROM fmcg_FactPromotion p JOIN fmcg_DimDate d ON p.Date=d.Date
JOIN fmcg_DimProduct prod ON p.ProductKey=prod.ProductKey
JOIN fmcg_DimCategory cat ON p.CategoryKey=cat.CategoryKey
JOIN fmcg_DimChannel ch ON p.ChannelKey=ch.ChannelKey
GROUP BY p.CampaignKey,p.ProductKey,d.Year,prod.Product,cat.Category,ch.Channel;

CREATE VIEW innovation_review AS
WITH s AS (
 SELECT ProductKey, SUM(Revenue) Revenue,SUM(Units) Units,SUM(GrossProfit) GrossProfit FROM fmcg_FactSales
 WHERE Innovation=1 GROUP BY ProductKey
), d AS (SELECT ProductKey,SUM(ActiveStoreDays) ActiveStoreDays,SUM(EligibleStoreDays) EligibleStoreDays
 FROM fmcg_FactDistribution WHERE ProductKey IN(SELECT ProductKey FROM fmcg_DimProduct WHERE Innovation=1) GROUP BY ProductKey),
 t AS (SELECT ProductKey,SUM(TargetRevenue) TargetRevenue FROM fmcg_FactTargets GROUP BY ProductKey),
 p AS (SELECT ProductKey,SUM(Trials) Trials,SUM(RepeatWithin28d) Repeats FROM fmcg_FactInnovationPanel GROUP BY ProductKey)
SELECT prod.Product,prod.ProductKey,prod.LaunchDate,s.Revenue,s.Units,s.GrossProfit,1.0*s.GrossProfit/s.Revenue GrossMargin,
 1.0*s.Units/d.ActiveStoreDays Velocity,1.0*d.ActiveStoreDays/d.EligibleStoreDays Distribution,
 1.0*s.Revenue/t.TargetRevenue TargetAttainment,p.Trials,p.Repeats,1.0*p.Repeats/p.Trials CohortRepeatRate,
 'SYNTHETIC_DERIVED' DataClass
FROM s JOIN fmcg_DimProduct prod USING(ProductKey) JOIN d USING(ProductKey) JOIN t USING(ProductKey) JOIN p USING(ProductKey);

CREATE VIEW revenue_bridge AS
WITH base AS (
 SELECT ProductKey,CustomerKey,
 SUM(CASE WHEN Year=2023 THEN Units ELSE 0 END) U0,
 SUM(CASE WHEN Year=2024 THEN Units ELSE 0 END) U1,
 SUM(CASE WHEN Year=2023 THEN Revenue ELSE 0 END) R0,
 SUM(CASE WHEN Year=2024 THEN Revenue ELSE 0 END) R1
 FROM commercial_sales GROUP BY ProductKey,CustomerKey
), rates AS (SELECT *,R0/NULLIF(U0,0) P0,R1/NULLIF(U1,0) P1 FROM base)
SELECT ProductKey,CustomerKey,R1-R0 RevenueDelta,
 CASE WHEN U0>0 THEN (U1-U0)*P0 ELSE 0 END VolumeEffect,
 CASE WHEN U0>0 THEN U0*(P1-P0) ELSE 0 END PriceMixEffect,
 CASE WHEN U0>0 THEN (U1-U0)*(P1-P0) ELSE 0 END InteractionEffect,
 CASE WHEN U0=0 THEN R1 ELSE 0 END NewProductEffect,
 'SYNTHETIC_DERIVED' DataClass FROM rates;

CREATE VIEW f1_execution AS
SELECT x.*,r.Season,r.Round,r.Race,r.Date,r.CircuitKey,c.Circuit,d.Driver,t.Constructor,
 q.QualifyingPosition,
 CASE x.Grid WHEN 1 THEN 25 WHEN 2 THEN 18 WHEN 3 THEN 15 WHEN 4 THEN 12 WHEN 5 THEN 10
 WHEN 6 THEN 8 WHEN 7 THEN 6 WHEN 8 THEN 4 WHEN 9 THEN 2 WHEN 10 THEN 1 ELSE 0 END GridPointsBenchmark,
 CASE WHEN x.ClassifiedFinish=0 THEN 1 ELSE 0 END NonFinish,
 CASE WHEN x.FinishPosition<=3 THEN 1 ELSE 0 END Podium,
 CASE WHEN x.FinishPosition=1 THEN 1 ELSE 0 END Win
FROM f1_FactRaceResults x JOIN f1_DimRace r USING(RaceKey) JOIN f1_DimCircuit c USING(CircuitKey)
JOIN f1_DimDriver d USING(DriverKey) JOIN f1_DimConstructor t USING(ConstructorKey)
LEFT JOIN f1_FactQualifying q ON x.RaceKey=q.RaceKey AND x.DriverKey=q.DriverKey;

CREATE VIEW driver_intelligence AS
SELECT Season,DriverKey,Driver,COUNT(*) Starts,SUM(Points) GPPoints,SUM(Win) Wins,SUM(Podium) Podiums,
 SUM(NonFinish) NonFinishes,AVG(QualifyingPosition) AvgQualifying,AVG(FinishPosition) AvgFinish,
 AVG(PositionGain) AvgClassifiedPositionGain,COUNT(PositionGain) EligibleMovementStarts,
 SUM(Points-GridPointsBenchmark) GPPointsAboveGridBenchmark,
 AVG(CASE WHEN ClassifiedFinish=1 THEN FinishPosition END) AvgClassifiedFinish,
 'PUBLIC_DERIVED' DataClass FROM f1_execution GROUP BY Season,DriverKey,Driver;

CREATE VIEW teammate_comparison AS
SELECT a.Season,a.DriverKey,a.Driver,COUNT(*) ComparableStarts,
 SUM(CASE WHEN a.FinishPosition<b.FinishPosition THEN 1 ELSE 0 END) AheadFinishes,
 AVG(a.Points-b.Points) AvgGPPointsAdvantage,
 'PUBLIC_DERIVED' DataClass
FROM f1_execution a JOIN f1_execution b ON a.RaceKey=b.RaceKey AND a.ConstructorKey=b.ConstructorKey AND a.DriverKey<>b.DriverKey
WHERE a.ClassifiedFinish=1 AND b.ClassifiedFinish=1
GROUP BY a.Season,a.DriverKey,a.Driver;

CREATE VIEW gp_points_progression AS
SELECT RaceKey,Season,Round,DriverKey,Driver,Points,
 SUM(Points) OVER(PARTITION BY Season,DriverKey ORDER BY Round ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) CumulativeGPPoints,
 'PUBLIC_DERIVED' DataClass FROM f1_execution;

CREATE VIEW pit_consistency AS
WITH filtered AS (
 SELECT p.*,r.Season,c.Constructor,
 ROW_NUMBER() OVER(PARTITION BY r.Season,p.ConstructorKey ORDER BY DurationSeconds) rn,
 COUNT(*) OVER(PARTITION BY r.Season,p.ConstructorKey) n
 FROM f1_FactPitStops p JOIN f1_DimRace r USING(RaceKey) JOIN f1_DimConstructor c USING(ConstructorKey)
 WHERE TimingEligible=1
)
SELECT Season,ConstructorKey,Constructor,COUNT(*) EligibleStops,AVG(DurationSeconds) MeanPitDuration,
 AVG(CASE WHEN rn IN ((n+1)/2,(n+2)/2) THEN DurationSeconds END) MedianPitDuration,
 AVG(DurationSeconds*DurationSeconds)-AVG(DurationSeconds)*AVG(DurationSeconds) PopulationVariance,
 MIN(DurationSeconds) MinDuration,MAX(DurationSeconds) MaxDuration,
 'PUBLIC_DERIVED' DataClass FROM filtered GROUP BY Season,ConstructorKey,Constructor;
