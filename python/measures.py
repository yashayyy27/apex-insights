"""DAX expressions authored into semantic models and generated reference docs.

These are source definitions, not claims of Analysis Services runtime validation.
Every measure has an interpretation/denominator note.
"""
MONEY = '$#,0;($#,0);$0'
PERCENT = '0.0%;-0.0%;0.0%'
NUMBER = '#,0.0'

def m(name, expression, fmt, folder, note):
    return dict(name=name, expression=expression, formatString=fmt, displayFolder=folder, description=note)

FMCG = [
 m('Revenue','SUM(FactSales[Revenue])',MONEY,'01 Performance','Synthetic AUD ex GST net revenue; trade spend is accounted separately.'),
 m('Units','SUM(FactSales[Units])','#,0','01 Performance','Individual packs sold, not unit cases.'),
 m('Volume Litres','SUM(FactSales[VolumeLitres])','#,0','01 Performance','Units times pack millilitres / 1000.'),
 m('COGS','SUM(FactSales[COGS])',MONEY,'01 Performance','Simulated variable product cost, excluding trade spend.'),
 m('Gross Profit','[Revenue] - [COGS]',MONEY,'01 Performance','Before trade spend and overheads.'),
 m('Gross Margin %','DIVIDE([Gross Profit],[Revenue])',PERCENT,'01 Performance','Ratio of totals, never an average of row percentages.'),
 m('Average Selling Price','DIVIDE([Revenue],[Units])','$0.00','01 Performance','AUD per pack. Mix effects mean it is not a pure price index.'),
 m('Revenue LY','CALCULATE([Revenue], SAMEPERIODLASTYEAR(DimDate[Date]))',MONEY,'02 Time','Same calendar dates one year earlier; first-year comparison is blank.'),
 m('Revenue YoY %','IF(HASONEVALUE(DimDate[Year]),DIVIDE([Revenue] - [Revenue LY],[Revenue LY]))',PERCENT,'02 Time','Growth relative to matching prior-year revenue; blank unless one calendar year is selected.'),
 m('Revenue YTD','CALCULATE([Revenue], DATESYTD(DimDate[Date]))',MONEY,'02 Time','Calendar-year cumulative revenue.'),
 m('Volume LY','CALCULATE([Volume Litres], DATEADD(DimDate[Date],-1,YEAR))','#,0','02 Time','Calendar-aligned prior-year volume.'),
 m('Volume Growth %','IF(HASONEVALUE(DimDate[Year]),DIVIDE([Volume Litres]-[Volume LY],[Volume LY]))',PERCENT,'02 Time','Litres growth; blank unless one calendar year is selected.'),
 m('Rolling 4 Week Sales','VAR EndDate = MAX(DimDate[Date]) RETURN CALCULATE([Revenue],DATESINPERIOD(DimDate[Date],EndDate,-28,DAY))',MONEY,'02 Time','28 calendar days inclusive of the selected end date.'),
 m('Rolling 13 Week Sales','VAR EndDate = MAX(DimDate[Date]) RETURN CALCULATE([Revenue],DATESINPERIOD(DimDate[Date],EndDate,-91,DAY))',MONEY,'02 Time','91 calendar days; periods near start of dataset are partial.'),
 m('Target Revenue','SUM(FactTargets[TargetRevenue])',MONEY,'03 Plan','Independent pre-period expectation; same product/customer/date grain as sales.'),
 m('Revenue vs Target','[Revenue]-[Target Revenue]',MONEY,'03 Plan','Absolute AUD gap.'),
 m('Target Attainment %','DIVIDE([Revenue],[Target Revenue])',PERCENT,'03 Plan','Ratios only within the same fact scope.'),
 m('Revenue Contribution %','DIVIDE([Revenue],CALCULATE([Revenue],REMOVEFILTERS(DimProduct),REMOVEFILTERS(DimCategory)))',PERCENT,'04 Category','Contribution within selected date/channel/region/customer scope; removes product/category filters.'),
 m('Selected Product Contribution %','DIVIDE([Revenue],CALCULATE([Revenue],ALLSELECTED(DimProduct)))',PERCENT,'04 Category','Share of products in current user selection; keeps category and other dimensions.'),
 m('Market Revenue','IF(ISFILTERED(DimProduct) || ISFILTERED(DimCustomer),BLANK(),SUM(FactMarket[MarketRevenue]))',MONEY,'04 Category','Synthetic market at date/category/channel/region grain. Blank under SKU or customer filters.'),
 m('Simulated Market Share %','DIVIDE([Revenue],[Market Revenue])',PERCENT,'04 Category','Generated market dollars denominator; no factual CCEP market-share claim.'),
 m('Simulated Share LY','CALCULATE([Simulated Market Share %],SAMEPERIODLASTYEAR(DimDate[Date]))',PERCENT,'04 Category','Matching calendar-year simulated share.'),
 m('Share Change pp','100*([Simulated Market Share %]-[Simulated Share LY])','0.00 "pp"','04 Category','Percentage-point change; blank if either share is unavailable.'),
 m('Active Store Days','SUM(FactDistribution[ActiveStoreDays])','#,0','05 Distribution','Additive SKU-store-days; not distinct physical stores.'),
 m('Eligible Store Days','SUM(FactDistribution[EligibleStoreDays])','#,0','05 Distribution','Universe of eligible SKU-store-day opportunities.'),
 m('Distribution %','DIVIDE([Active Store Days],[Eligible Store Days])',PERCENT,'05 Distribution','Weighted distribution proxy. Does not estimate ACV distribution.'),
 m('Velocity','DIVIDE([Units],[Active Store Days])','0.00','05 Distribution','Units per active SKU-store-day; preserves exposure when summing dates/SKUs.'),
 m('Revenue per Active Store Day','DIVIDE([Revenue],[Active Store Days])','$0.00','05 Distribution','Revenue per active SKU-store-day.'),
 m('SKU Revenue Rank','RANKX(ALLSELECTED(DimProduct[Product]),[Revenue],,DESC,DENSE)','0','05 Distribution','Rank within selected product universe.'),
 m('Trade Spend','SUM(FactSales[TradeSpend])',MONEY,'06 Promotion','Campaign execution spend; discounts are already inside net revenue.'),
 m('Baseline Units','SUM(FactPromotion[BaselineUnits])','#,0','06 Promotion','Generator counterfactual only for promoted product/customer/days.'),
 m('Promoted Units','SUM(FactPromotion[ActualUnits])','#,0','06 Promotion','Same promoted population as baseline.'),
 m('Incremental Units','[Promoted Units]-[Baseline Units]','#,0','06 Promotion','Simulated incremental units, not real experimentally measured lift.'),
 m('Promotion Lift %','DIVIDE([Incremental Units],[Baseline Units])',PERCENT,'06 Promotion','Counterfactual same-period simulated lift.'),
 m('Incremental Sales','SUM(FactPromotion[ActualRevenue])-SUM(FactPromotion[BaselineRevenue])',MONEY,'06 Promotion','Net revenue delta includes lower realised prices.'),
 m('Net Incremental Promotion Profit','SUM(FactPromotion[NetIncrementalProfit])',MONEY,'06 Promotion','Actual GP minus baseline GP minus trade spend; no double-counted discount expense.'),
 m('Promotion ROI','DIVIDE([Net Incremental Promotion Profit],SUM(FactPromotion[TradeSpend]))','0.00"x"','06 Promotion','Net incremental profit per AUD of execution spend; can be negative.'),
 m('Discount Depth %','DIVIDE(SUMX(FactPromotion,FactPromotion[DiscountDepth]*FactPromotion[ActualUnits]),[Promoted Units])',PERCENT,'06 Promotion','Unit-weighted discount depth for promoted observations only.'),
 m('Innovation Revenue','CALCULATE([Revenue],KEEPFILTERS(DimProduct[Innovation]=1))',MONEY,'07 Innovation','Sales from the two simulated 2024 launches.'),
 m('Innovation Contribution %','DIVIDE([Innovation Revenue],[Revenue])',PERCENT,'07 Innovation','Launch revenue share of selected revenue.'),
 m('Cohort Repeat Rate %','DIVIDE(SUM(FactInnovationPanel[RepeatWithin28d]),SUM(FactInnovationPanel[Trials]))',PERCENT,'07 Innovation','Trials-weighted 28-day repeat; cohorts with incomplete follow-up excluded in ETL.'),
 m('Distribution Opportunity Revenue','VAR CurrentDist=[Distribution %] VAR DesiredDist=SELECTEDVALUE(DistributionGoal[Value],0.70) RETURN IF(CurrentDist>0,[Revenue]*MAX(0,DesiredDist-CurrentDist)/CurrentDist)',MONEY,'08 Scenarios','SIMULATION: same velocity, price and period, incremental distribution only; no cannibalisation or costs.'),
 m('Selected KPI','SWITCH(SELECTEDVALUE(KPISelector[KPI],"Revenue"),"Revenue",[Revenue],"Gross margin",[Gross Margin %],"Velocity",[Velocity],"Target attainment",[Target Attainment %])',NUMBER,'08 Scenarios','Disconnected KPI selector; dynamic format keeps money, percentages and exposure distinct.'),
 m('Dynamic Title','"SYNTHETIC | " & SELECTEDVALUE(KPISelector[KPI],"Revenue") & " | " & IF(HASONEVALUE(DimCategory[Category]),SELECTEDVALUE(DimCategory[Category]),"Selected categories")','@','08 Scenarios','Title always retains synthetic status.'),
 m('Variance Colour','IF([Revenue vs Target]<0,"#BA3548","#087F70")','@','08 Scenarios','Used by conditional formatting for a plan gap; does not encode a causal claim.'),
]

F1 = [
 m('GP Points','SUM(FactRaceResults[Points])','#,0','01 Championship','Grand Prix points only; includes fastest-lap points recorded by source.'),
 m('Sprint Points','SUM(FactSprintResults[Points])','#,0','01 Championship','Sprint points separately ingested.'),
 m('Total Recorded Points','[GP Points]+[Sprint Points]','#,0','01 Championship','Session-result total reconciled against official standings.'),
 m('Official Driver Points','IF(ISFILTERED(DimRace)||ISFILTERED(DimCircuit)||ISFILTERED(DimConstructor),BLANK(),SUM(FactDriverStandings[Points]))','#,0','01 Championship','Final season standings, not filtered-race accumulation. Blank under race/circuit/constructor filters.'),
 m('Official Constructor Points','IF(ISFILTERED(DimRace)||ISFILTERED(DimCircuit)||ISFILTERED(DimDriver),BLANK(),SUM(FactConstructorStandings[Points]))','#,0','01 Championship','Official final constructor standings; driver filter has no meaningful denominator.'),
 m('Starts','COUNTROWS(FactRaceResults)','#,0','02 Execution','Driver-race entries; a constructor generally has two entries per Grand Prix.'),
 m('Wins','CALCULATE([Starts],FactRaceResults[FinishPosition]=1)','#,0','02 Execution','GP wins from classified position.'),
 m('Podiums','CALCULATE([Starts],FactRaceResults[FinishPosition]<=3)','#,0','02 Execution','GP classified top three.'),
 m('Non-finishes','CALCULATE([Starts],FactRaceResults[ClassifiedFinish]=0)','#,0','03 Reliability','Status excludes Finished/Lapped and legacy +N Lap(s). Includes retirement, DNS and DSQ; not all mechanical.'),
 m('Non-finish Rate %','DIVIDE([Non-finishes],[Starts])',PERCENT,'03 Reliability','Observed non-completion proxy, not engineering reliability probability.'),
 m('Average Grid','AVERAGEX(FILTER(FactRaceResults,FactRaceResults[Grid]>0),FactRaceResults[Grid])','0.00','02 Execution','Excludes grid 0 pit-lane starts.'),
 m('Average Finish','AVERAGE(FactRaceResults[FinishPosition])','0.00','02 Execution','Includes all classified positions assigned by source, including nonfinishers.'),
 m('Average Qualifying Position','AVERAGE(FactQualifying[QualifyingPosition])','0.00','02 Execution','Ordinal result; not lap-time pace measured across dissimilar sessions.'),
 m('Classified Position Gain','AVERAGE(FactRaceResults[PositionGain])','0.00','02 Execution','Mean grid minus finish for finish/+lap status and nonzero grids only.'),
 m('Movement Eligible Starts','COUNT(FactRaceResults[PositionGain])','#,0','02 Execution','Denominator for movement; DNF exclusion creates survivorship bias.'),
 m('Teammate Comparable Starts','SUMX(FILTER(FactRaceResults,FactRaceResults[ClassifiedFinish]=1),VAR RaceID=FactRaceResults[RaceKey] VAR TeamID=FactRaceResults[ConstructorKey] VAR DriverID=FactRaceResults[DriverKey] VAR Opponent=FILTER(ALL(FactRaceResults),FactRaceResults[RaceKey]=RaceID&&FactRaceResults[ConstructorKey]=TeamID&&FactRaceResults[DriverKey]<>DriverID&&FactRaceResults[ClassifiedFinish]=1) RETURN IF(COUNTROWS(Opponent)=1,1,0))','#,0','02 Execution','Driver-race comparisons with exactly one teammate and both finish/+lap statuses. Uses actual constructor at that race; opponent lookup ignores current driver filter. Survivor bias remains.'),
 m('Teammate Ahead Finishes','SUMX(FILTER(FactRaceResults,FactRaceResults[ClassifiedFinish]=1),VAR RaceID=FactRaceResults[RaceKey] VAR TeamID=FactRaceResults[ConstructorKey] VAR DriverID=FactRaceResults[DriverKey] VAR Finish=FactRaceResults[FinishPosition] VAR Opponent=FILTER(ALL(FactRaceResults),FactRaceResults[RaceKey]=RaceID&&FactRaceResults[ConstructorKey]=TeamID&&FactRaceResults[DriverKey]<>DriverID&&FactRaceResults[ClassifiedFinish]=1) RETURN IF(COUNTROWS(Opponent)=1&&Finish<MINX(Opponent,FactRaceResults[FinishPosition]),1,0))','#,0','02 Execution','Ahead count within shared completed races. Total across both teammates counts one ahead result per comparable pair.'),
 m('Teammate Ahead Rate %','DIVIDE([Teammate Ahead Finishes],[Teammate Comparable Starts])',PERCENT,'02 Execution','Shared-completion ahead rate; show the comparable-start denominator. This does not isolate underlying pace or estimate a causal driver effect.'),
 m('GP Points Above Grid Benchmark','SUMX(FactRaceResults,VAR G=FactRaceResults[Grid] VAR P=SWITCH(G,1,25,2,18,3,15,4,12,5,10,6,8,7,6,8,4,9,2,10,1,0) RETURN FactRaceResults[Points]-P)','#,0','02 Execution','Actual GP points minus standard points if finishing at grid. Descriptive benchmark, no causal lost-points claim.'),
 m('Cumulative GP Points','VAR LastRound=MAX(DimRace[Round]) VAR Season=SELECTEDVALUE(DimSeason[Season]) RETURN IF(NOT ISBLANK(Season),CALCULATE([GP Points],FILTER(ALL(DimRace),DimRace[Season]=Season&&DimRace[Round]<=LastRound)))','#,0','01 Championship','Single-season cumulative GP points; explicitly excludes sprints, preserves driver/constructor selection.'),
 m('Points per Start','DIVIDE([GP Points],[Starts])','0.00','02 Execution','Uses all race entries.'),
 m('Driver Points Rank','RANKX(ALLSELECTED(DimDriver[Driver]),[Total Recorded Points],,DESC,DENSE)','0','01 Championship','Selected recorded points, not official penalty-adjusted championship rank.'),
 m('Pit Stops','COUNTROWS(FactPitStops)','#,0','04 Pit stops','All recorded stops, including extreme durations retained for audit.'),
 m('Eligible Pit Stops','CALCULATE([Pit Stops],FactPitStops[TimingEligible]=1)','#,0','04 Pit stops','Duration 10–60 seconds, transparent analytical screen.'),
 m('Median Pit Duration','CALCULATE(MEDIAN(FactPitStops[DurationSeconds]),FactPitStops[TimingEligible]=1)','0.000 "s"','04 Pit stops','API pit duration, not stationary wheel-change time. Circuit pit-lane lengths differ.'),
 m('Pit Duration StdDev','CALCULATE(STDEV.P(FactPitStops[DurationSeconds]),FactPitStops[TimingEligible]=1)','0.000 "s"','04 Pit stops','Dispersion across eligible stops. Compare within race before judging a team.'),
 m('Median Pit Window','MEDIAN(FactPitStops[LapFraction])',PERCENT,'04 Pit stops','Pit lap / driver completed race laps; denominator can be shortened by retirement.'),
 m('Sample Lap Observations','COUNTROWS(FactLaps)','#,0','05 Sample laps','Only Bahrain and Monaco 2024; all laps retained, no claimed clean-air telemetry.'),
 m('Median Sample Lap','MEDIAN(FactLaps[LapSeconds])','0.000 "s"','05 Sample laps','Raw lap median; safety cars, traffic and pit laps are confounders.'),
 m('Scenario Pit Cost','SELECTEDVALUE(StopCount[Value],2)*SELECTEDVALUE(PitLoss[Value],22)','0.0 "s"','06 Strategy simulation','SIMULATION: assumed number of stops × assumed pit loss.'),
 m('Scenario Degradation Cost','VAR N=SELECTEDVALUE(RaceLaps[Value],60) VAR S=SELECTEDVALUE(StopCount[Value],2)+1 VAR Q=INT(N/S) VAR R=MOD(N,S) VAR D=SELECTEDVALUE(Degradation[Value],0.05) RETURN D*((S-R)*Q*(Q-1)/2+R*Q*(Q+1)/2)','0.0 "s"','06 Strategy simulation','SIMULATION: balanced integer stints; lap penalty accumulates linearly and resets at each stop.'),
 m('Scenario Added Time','[Scenario Pit Cost]+[Scenario Degradation Cost]','0.0 "s"','06 Strategy simulation','SIMULATION: relative to constant fresh-tyre lap baseline; no finishing-position prediction.'),
 m('Scenario Title','"SIMULATION | " & FORMAT(SELECTEDVALUE(StopCount[Value],2),"0") & " stops | No outcome prediction"','@','06 Strategy simulation','Always displays simulation status.'),
]

# Fix explicit blank semantics: subtraction otherwise treats BLANK as zero.
for measure in FMCG:
    if measure['name'] == 'Share Change pp':
        measure['expression'] = 'VAR CurrentShare=[Simulated Market Share %] VAR PriorShare=[Simulated Share LY] RETURN IF(HASONEVALUE(DimDate[Year])&&NOT ISBLANK(CurrentShare)&&NOT ISBLANK(PriorShare),100*(CurrentShare-PriorShare))'
    if measure['name'] == 'Selected KPI':
        measure['formatStringDefinition'] = {'expression': 'SWITCH(SELECTEDVALUE(KPISelector[KPI],"Revenue"),"Revenue","$#,0","Gross margin","0.0%","Velocity","0.00","Target attainment","0.0%")'}
