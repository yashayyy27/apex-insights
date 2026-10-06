# DAX measure library

These measures exist in the native `model.bim` files. Source authored; runtime evaluation pending Windows acceptance.

## Commercial — ALL SYNTHETIC

### Revenue

Synthetic AUD ex GST net revenue; trade spend is accounted separately.

```dax
Revenue =
SUM(FactSales[Revenue])
```

### Units

Individual packs sold, not unit cases.

```dax
Units =
SUM(FactSales[Units])
```

### Volume Litres

Units times pack millilitres / 1000.

```dax
Volume Litres =
SUM(FactSales[VolumeLitres])
```

### COGS

Simulated variable product cost, excluding trade spend.

```dax
COGS =
SUM(FactSales[COGS])
```

### Gross Profit

Before trade spend and overheads.

```dax
Gross Profit =
[Revenue] - [COGS]
```

### Gross Margin %

Ratio of totals, never an average of row percentages.

```dax
Gross Margin % =
DIVIDE([Gross Profit],[Revenue])
```

### Average Selling Price

AUD per pack. Mix effects mean it is not a pure price index.

```dax
Average Selling Price =
DIVIDE([Revenue],[Units])
```

### Revenue LY

Same calendar dates one year earlier; first-year comparison is blank.

```dax
Revenue LY =
CALCULATE([Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))
```

### Revenue YoY %

Growth relative to matching prior-year revenue; blank unless one calendar year is selected.

```dax
Revenue YoY % =
IF(HASONEVALUE(DimDate[Year]),DIVIDE([Revenue] - [Revenue LY],[Revenue LY]))
```

### Revenue YTD

Calendar-year cumulative revenue.

```dax
Revenue YTD =
CALCULATE([Revenue], DATESYTD(DimDate[Date]))
```

### Volume LY

Calendar-aligned prior-year volume.

```dax
Volume LY =
CALCULATE([Volume Litres], DATEADD(DimDate[Date],-1,YEAR))
```

### Volume Growth %

Litres growth; blank unless one calendar year is selected.

```dax
Volume Growth % =
IF(HASONEVALUE(DimDate[Year]),DIVIDE([Volume Litres]-[Volume LY],[Volume LY]))
```

### Rolling 4 Week Sales

28 calendar days inclusive of the selected end date.

```dax
Rolling 4 Week Sales =
VAR EndDate = MAX(DimDate[Date]) RETURN CALCULATE([Revenue],DATESINPERIOD(DimDate[Date],EndDate,-28,DAY))
```

### Rolling 13 Week Sales

91 calendar days; periods near start of dataset are partial.

```dax
Rolling 13 Week Sales =
VAR EndDate = MAX(DimDate[Date]) RETURN CALCULATE([Revenue],DATESINPERIOD(DimDate[Date],EndDate,-91,DAY))
```

### Target Revenue

Independent pre-period expectation; same product/customer/date grain as sales.

```dax
Target Revenue =
SUM(FactTargets[TargetRevenue])
```

### Revenue vs Target

Absolute AUD gap.

```dax
Revenue vs Target =
[Revenue]-[Target Revenue]
```

### Target Attainment %

Ratios only within the same fact scope.

```dax
Target Attainment % =
DIVIDE([Revenue],[Target Revenue])
```

### Revenue Contribution %

Contribution within selected date/channel/region/customer scope; removes product/category filters.

```dax
Revenue Contribution % =
DIVIDE([Revenue],CALCULATE([Revenue],REMOVEFILTERS(DimProduct),REMOVEFILTERS(DimCategory)))
```

### Selected Product Contribution %

Share of products in current user selection; keeps category and other dimensions.

```dax
Selected Product Contribution % =
DIVIDE([Revenue],CALCULATE([Revenue],ALLSELECTED(DimProduct)))
```

### Market Revenue

Synthetic market at date/category/channel/region grain. Blank under SKU or customer filters.

```dax
Market Revenue =
IF(ISFILTERED(DimProduct) || ISFILTERED(DimCustomer),BLANK(),SUM(FactMarket[MarketRevenue]))
```

### Simulated Market Share %

Generated market dollars denominator; no factual CCEP market-share claim.

```dax
Simulated Market Share % =
DIVIDE([Revenue],[Market Revenue])
```

### Simulated Share LY

Matching calendar-year simulated share.

```dax
Simulated Share LY =
CALCULATE([Simulated Market Share %],SAMEPERIODLASTYEAR(DimDate[Date]))
```

### Share Change pp

Percentage-point change; blank if either share is unavailable.

```dax
Share Change pp =
VAR CurrentShare=[Simulated Market Share %] VAR PriorShare=[Simulated Share LY] RETURN IF(HASONEVALUE(DimDate[Year])&&NOT ISBLANK(CurrentShare)&&NOT ISBLANK(PriorShare),100*(CurrentShare-PriorShare))
```

### Active Store Days

Additive SKU-store-days; not distinct physical stores.

```dax
Active Store Days =
SUM(FactDistribution[ActiveStoreDays])
```

### Eligible Store Days

Universe of eligible SKU-store-day opportunities.

```dax
Eligible Store Days =
SUM(FactDistribution[EligibleStoreDays])
```

### Distribution %

Weighted distribution proxy. Does not estimate ACV distribution.

```dax
Distribution % =
DIVIDE([Active Store Days],[Eligible Store Days])
```

### Velocity

Units per active SKU-store-day; preserves exposure when summing dates/SKUs.

```dax
Velocity =
DIVIDE([Units],[Active Store Days])
```

### Revenue per Active Store Day

Revenue per active SKU-store-day.

```dax
Revenue per Active Store Day =
DIVIDE([Revenue],[Active Store Days])
```

### SKU Revenue Rank

Rank within selected product universe.

```dax
SKU Revenue Rank =
RANKX(ALLSELECTED(DimProduct[Product]),[Revenue],,DESC,DENSE)
```

### Trade Spend

Campaign execution spend; discounts are already inside net revenue.

```dax
Trade Spend =
SUM(FactSales[TradeSpend])
```

### Baseline Units

Generator counterfactual only for promoted product/customer/days.

```dax
Baseline Units =
SUM(FactPromotion[BaselineUnits])
```

### Promoted Units

Same promoted population as baseline.

```dax
Promoted Units =
SUM(FactPromotion[ActualUnits])
```

### Incremental Units

Simulated incremental units, not real experimentally measured lift.

```dax
Incremental Units =
[Promoted Units]-[Baseline Units]
```

### Promotion Lift %

Counterfactual same-period simulated lift.

```dax
Promotion Lift % =
DIVIDE([Incremental Units],[Baseline Units])
```

### Incremental Sales

Net revenue delta includes lower realised prices.

```dax
Incremental Sales =
SUM(FactPromotion[ActualRevenue])-SUM(FactPromotion[BaselineRevenue])
```

### Net Incremental Promotion Profit

Actual GP minus baseline GP minus trade spend; no double-counted discount expense.

```dax
Net Incremental Promotion Profit =
SUM(FactPromotion[NetIncrementalProfit])
```

### Promotion ROI

Net incremental profit per AUD of execution spend; can be negative.

```dax
Promotion ROI =
DIVIDE([Net Incremental Promotion Profit],SUM(FactPromotion[TradeSpend]))
```

### Discount Depth %

Unit-weighted discount depth for promoted observations only.

```dax
Discount Depth % =
DIVIDE(SUMX(FactPromotion,FactPromotion[DiscountDepth]*FactPromotion[ActualUnits]),[Promoted Units])
```

### Innovation Revenue

Sales from the two simulated 2024 launches.

```dax
Innovation Revenue =
CALCULATE([Revenue],KEEPFILTERS(DimProduct[Innovation]=1))
```

### Innovation Contribution %

Launch revenue share of selected revenue.

```dax
Innovation Contribution % =
DIVIDE([Innovation Revenue],[Revenue])
```

### Cohort Repeat Rate %

Trials-weighted 28-day repeat; cohorts with incomplete follow-up excluded in ETL.

```dax
Cohort Repeat Rate % =
DIVIDE(SUM(FactInnovationPanel[RepeatWithin28d]),SUM(FactInnovationPanel[Trials]))
```

### Distribution Opportunity Revenue

SIMULATION: same velocity, price and period, incremental distribution only; no cannibalisation or costs.

```dax
Distribution Opportunity Revenue =
VAR CurrentDist=[Distribution %] VAR DesiredDist=SELECTEDVALUE(DistributionGoal[Value],0.70) RETURN IF(CurrentDist>0,[Revenue]*MAX(0,DesiredDist-CurrentDist)/CurrentDist)
```

### Selected KPI

Disconnected KPI selector; dynamic format keeps money, percentages and exposure distinct.

```dax
Selected KPI =
SWITCH(SELECTEDVALUE(KPISelector[KPI],"Revenue"),"Revenue",[Revenue],"Gross margin",[Gross Margin %],"Velocity",[Velocity],"Target attainment",[Target Attainment %])
```

### Dynamic Title

Title always retains synthetic status.

```dax
Dynamic Title =
"SYNTHETIC | " & SELECTEDVALUE(KPISelector[KPI],"Revenue") & " | " & IF(HASONEVALUE(DimCategory[Category]),SELECTEDVALUE(DimCategory[Category]),"Selected categories")
```

### Variance Colour

Used by conditional formatting for a plan gap; does not encode a causal claim.

```dax
Variance Colour =
IF([Revenue vs Target]<0,"#BA3548","#087F70")
```

## F1 — PUBLIC_DERIVED; Strategy Lab SIMULATION

### GP Points

Grand Prix points only; includes fastest-lap points recorded by source.

```dax
GP Points =
SUM(FactRaceResults[Points])
```

### Sprint Points

Sprint points separately ingested.

```dax
Sprint Points =
SUM(FactSprintResults[Points])
```

### Total Recorded Points

Session-result total reconciled against official standings.

```dax
Total Recorded Points =
[GP Points]+[Sprint Points]
```

### Official Driver Points

Final season standings, not filtered-race accumulation. Blank under race/circuit/constructor filters.

```dax
Official Driver Points =
IF(ISFILTERED(DimRace)||ISFILTERED(DimCircuit)||ISFILTERED(DimConstructor),BLANK(),SUM(FactDriverStandings[Points]))
```

### Official Constructor Points

Official final constructor standings; driver filter has no meaningful denominator.

```dax
Official Constructor Points =
IF(ISFILTERED(DimRace)||ISFILTERED(DimCircuit)||ISFILTERED(DimDriver),BLANK(),SUM(FactConstructorStandings[Points]))
```

### Starts

Driver-race entries; a constructor generally has two entries per Grand Prix.

```dax
Starts =
COUNTROWS(FactRaceResults)
```

### Wins

GP wins from classified position.

```dax
Wins =
CALCULATE([Starts],FactRaceResults[FinishPosition]=1)
```

### Podiums

GP classified top three.

```dax
Podiums =
CALCULATE([Starts],FactRaceResults[FinishPosition]<=3)
```

### Non-finishes

Status excludes Finished/Lapped and legacy +N Lap(s). Includes retirement, DNS and DSQ; not all mechanical.

```dax
Non-finishes =
CALCULATE([Starts],FactRaceResults[ClassifiedFinish]=0)
```

### Non-finish Rate %

Observed non-completion proxy, not engineering reliability probability.

```dax
Non-finish Rate % =
DIVIDE([Non-finishes],[Starts])
```

### Average Grid

Excludes grid 0 pit-lane starts.

```dax
Average Grid =
AVERAGEX(FILTER(FactRaceResults,FactRaceResults[Grid]>0),FactRaceResults[Grid])
```

### Average Finish

Includes all classified positions assigned by source, including nonfinishers.

```dax
Average Finish =
AVERAGE(FactRaceResults[FinishPosition])
```

### Average Qualifying Position

Ordinal result; not lap-time pace measured across dissimilar sessions.

```dax
Average Qualifying Position =
AVERAGE(FactQualifying[QualifyingPosition])
```

### Classified Position Gain

Mean grid minus finish for finish/+lap status and nonzero grids only.

```dax
Classified Position Gain =
AVERAGE(FactRaceResults[PositionGain])
```

### Movement Eligible Starts

Denominator for movement; DNF exclusion creates survivorship bias.

```dax
Movement Eligible Starts =
COUNT(FactRaceResults[PositionGain])
```

### Teammate Comparable Starts

Driver-race comparisons with exactly one teammate and both finish/+lap statuses. Uses actual constructor at that race; opponent lookup ignores current driver filter. Survivor bias remains.

```dax
Teammate Comparable Starts =
SUMX(FILTER(FactRaceResults,FactRaceResults[ClassifiedFinish]=1),VAR RaceID=FactRaceResults[RaceKey] VAR TeamID=FactRaceResults[ConstructorKey] VAR DriverID=FactRaceResults[DriverKey] VAR Opponent=FILTER(ALL(FactRaceResults),FactRaceResults[RaceKey]=RaceID&&FactRaceResults[ConstructorKey]=TeamID&&FactRaceResults[DriverKey]<>DriverID&&FactRaceResults[ClassifiedFinish]=1) RETURN IF(COUNTROWS(Opponent)=1,1,0))
```

### Teammate Ahead Finishes

Ahead count within shared completed races. Total across both teammates counts one ahead result per comparable pair.

```dax
Teammate Ahead Finishes =
SUMX(FILTER(FactRaceResults,FactRaceResults[ClassifiedFinish]=1),VAR RaceID=FactRaceResults[RaceKey] VAR TeamID=FactRaceResults[ConstructorKey] VAR DriverID=FactRaceResults[DriverKey] VAR Finish=FactRaceResults[FinishPosition] VAR Opponent=FILTER(ALL(FactRaceResults),FactRaceResults[RaceKey]=RaceID&&FactRaceResults[ConstructorKey]=TeamID&&FactRaceResults[DriverKey]<>DriverID&&FactRaceResults[ClassifiedFinish]=1) RETURN IF(COUNTROWS(Opponent)=1&&Finish<MINX(Opponent,FactRaceResults[FinishPosition]),1,0))
```

### Teammate Ahead Rate %

Shared-completion ahead rate; show the comparable-start denominator. This does not isolate underlying pace or estimate a causal driver effect.

```dax
Teammate Ahead Rate % =
DIVIDE([Teammate Ahead Finishes],[Teammate Comparable Starts])
```

### GP Points Above Grid Benchmark

Actual GP points minus standard points if finishing at grid. Descriptive benchmark, no causal lost-points claim.

```dax
GP Points Above Grid Benchmark =
SUMX(FactRaceResults,VAR G=FactRaceResults[Grid] VAR P=SWITCH(G,1,25,2,18,3,15,4,12,5,10,6,8,7,6,8,4,9,2,10,1,0) RETURN FactRaceResults[Points]-P)
```

### Cumulative GP Points

Single-season cumulative GP points; explicitly excludes sprints, preserves driver/constructor selection.

```dax
Cumulative GP Points =
VAR LastRound=MAX(DimRace[Round]) VAR Season=SELECTEDVALUE(DimSeason[Season]) RETURN IF(NOT ISBLANK(Season),CALCULATE([GP Points],FILTER(ALL(DimRace),DimRace[Season]=Season&&DimRace[Round]<=LastRound)))
```

### Points per Start

Uses all race entries.

```dax
Points per Start =
DIVIDE([GP Points],[Starts])
```

### Driver Points Rank

Selected recorded points, not official penalty-adjusted championship rank.

```dax
Driver Points Rank =
RANKX(ALLSELECTED(DimDriver[Driver]),[Total Recorded Points],,DESC,DENSE)
```

### Pit Stops

All recorded stops, including extreme durations retained for audit.

```dax
Pit Stops =
COUNTROWS(FactPitStops)
```

### Eligible Pit Stops

Duration 10–60 seconds, transparent analytical screen.

```dax
Eligible Pit Stops =
CALCULATE([Pit Stops],FactPitStops[TimingEligible]=1)
```

### Median Pit Duration

API pit duration, not stationary wheel-change time. Circuit pit-lane lengths differ.

```dax
Median Pit Duration =
CALCULATE(MEDIAN(FactPitStops[DurationSeconds]),FactPitStops[TimingEligible]=1)
```

### Pit Duration StdDev

Dispersion across eligible stops. Compare within race before judging a team.

```dax
Pit Duration StdDev =
CALCULATE(STDEV.P(FactPitStops[DurationSeconds]),FactPitStops[TimingEligible]=1)
```

### Median Pit Window

Pit lap / driver completed race laps; denominator can be shortened by retirement.

```dax
Median Pit Window =
MEDIAN(FactPitStops[LapFraction])
```

### Sample Lap Observations

Only Bahrain and Monaco 2024; all laps retained, no claimed clean-air telemetry.

```dax
Sample Lap Observations =
COUNTROWS(FactLaps)
```

### Median Sample Lap

Raw lap median; safety cars, traffic and pit laps are confounders.

```dax
Median Sample Lap =
MEDIAN(FactLaps[LapSeconds])
```

### Scenario Pit Cost

SIMULATION: assumed number of stops × assumed pit loss.

```dax
Scenario Pit Cost =
SELECTEDVALUE(StopCount[Value],2)*SELECTEDVALUE(PitLoss[Value],22)
```

### Scenario Degradation Cost

SIMULATION: balanced integer stints; lap penalty accumulates linearly and resets at each stop.

```dax
Scenario Degradation Cost =
VAR N=SELECTEDVALUE(RaceLaps[Value],60) VAR S=SELECTEDVALUE(StopCount[Value],2)+1 VAR Q=INT(N/S) VAR R=MOD(N,S) VAR D=SELECTEDVALUE(Degradation[Value],0.05) RETURN D*((S-R)*Q*(Q-1)/2+R*Q*(Q+1)/2)
```

### Scenario Added Time

SIMULATION: relative to constant fresh-tyre lap baseline; no finishing-position prediction.

```dax
Scenario Added Time =
[Scenario Pit Cost]+[Scenario Degradation Cost]
```

### Scenario Title

Always displays simulation status.

```dax
Scenario Title =
"SIMULATION | " & FORMAT(SELECTEDVALUE(StopCount[Value],2),"0") & " stops | No outcome prediction"
```
