-- All should return zero rows (or numeric zero as named).
PRAGMA foreign_key_check;
SELECT Date,ProductKey,CustomerKey,COUNT(*) n FROM fmcg_FactSales
GROUP BY Date,ProductKey,CustomerKey HAVING n<>1;
SELECT COUNT(*) BadSalesMath FROM fmcg_FactSales
WHERE ABS(Revenue-Units*NetPrice)>0.011 OR ABS(GrossProfit-(Revenue-COGS))>0.011;
SELECT COUNT(*) BadDistribution FROM fmcg_FactDistribution
WHERE ActiveStoreDays<0 OR ActiveStoreDays>EligibleStoreDays;
SELECT ABS(SUM(RevenueDelta-VolumeEffect-PriceMixEffect-InteractionEffect-NewProductEffect)) BridgeResidual
FROM revenue_bridge;
SELECT RaceKey,FinishPosition,COUNT(*) n FROM f1_FactRaceResults
GROUP BY RaceKey,FinishPosition HAVING n<>1;
SELECT COUNT(*) MixedProvenance FROM fmcg_FactSales WHERE DataClass<>'SYNTHETIC';
-- Official standings reconciliation includes sprint points; exceptions must be investigated.
WITH gp AS (SELECT r.Season,x.DriverKey,SUM(x.Points) Points FROM f1_FactRaceResults x JOIN f1_DimRace r USING(RaceKey) GROUP BY r.Season,x.DriverKey),
sp AS (SELECT r.Season,x.DriverKey,SUM(x.Points) Points FROM f1_FactSprintResults x JOIN f1_DimRace r USING(RaceKey) GROUP BY r.Season,x.DriverKey)
SELECT s.Season,s.DriverKey,s.Points,COALESCE(gp.Points,0)+COALESCE(sp.Points,0) DerivedPoints
FROM f1_FactDriverStandings s LEFT JOIN gp USING(Season,DriverKey) LEFT JOIN sp USING(Season,DriverKey)
WHERE ABS(s.Points-COALESCE(gp.Points,0)-COALESCE(sp.Points,0))>0.001;
