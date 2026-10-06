# Data dictionary and grain contracts

Commercial data is wholly SYNTHETIC; public context and F1 are separate. Every input field is listed. Row counts reflect this snapshot.

## fmcg.DimCategory

Rows: 5. Key/grain: CategoryKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| CategoryKey | int64 | No | Stable conformed identifier. |
| Category | object | No | Fictional descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.DimChannel

Rows: 5. Key/grain: ChannelKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| ChannelKey | int64 | No | Stable conformed identifier. |
| Channel | object | No | Fictional descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.DimCustomer

Rows: 15. Key/grain: CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| CustomerKey | int64 | No | Stable conformed identifier. |
| Customer | object | No | Fictional descriptive attribute. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| EligibleStores | int64 | No | Fictional account store universe. Fixed for this scenario. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.DimDate

Rows: 731. Key/grain: Date.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| Year | int64 | No | Calendar attribute used for ordering/filtering; generated from Date. |
| MonthNumber | int64 | No | Calendar attribute used for ordering/filtering; generated from Date. |
| Month | object | No | Calendar attribute used for ordering/filtering; generated from Date. |
| YearMonth | object | No | Sortable YYYY-MM calendar month. |
| Quarter | object | No | Calendar attribute used for ordering/filtering; generated from Date. |
| WeekStart | object | No | Monday of week. Innovation cohort completeness counts from this date. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.DimProduct

Rows: 24. Key/grain: ProductKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| ProductKey | int64 | No | Stable conformed identifier. |
| Product | object | No | Fictional descriptive attribute. |
| Brand | object | No | Fictional descriptive attribute. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| Category | object | No | Fictional descriptive attribute. |
| PackMl | int64 | No | Millilitres per individual pack. |
| Innovation | int64 | No | 0 existing SKU, 1 a simulated 2024 launch. |
| LaunchDate | object | No | First sale eligibility. Products may not sell before this date. |
| RegularPrice | float64 | No | Base simulated pack price AUD before year/channel/promotion modifiers. |
| UnitCost | float64 | No | AUD variable cost per individual pack. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.DimRegion

Rows: 3. Key/grain: RegionKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RegionKey | int64 | No | Stable conformed identifier. |
| Region | object | No | Fictional descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.FactDistribution

Rows: 248,580. Key/grain: Date, ProductKey, CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| ProductKey | int64 | No | Stable conformed identifier. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| CustomerKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| ActiveStoreDays | int64 | No | One daily observation counts active stores for this SKU/account. Across dates/products, counts SKU-store-days, not distinct stores. |
| EligibleStoreDays | int64 | No | Eligible SKU-store-day exposure in the same grain/population. |
## fmcg.FactInnovationPanel

Rows: 930. Key/grain: Date, ProductKey, CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| ProductKey | int64 | No | Stable conformed identifier. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| CustomerKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| Trials | int64 | No | Distinct simulated trialists within each account/SKU/cohort; cohorts are independent. |
| RepeatWithin28d | int64 | No | Simulated trialists repeating within 28 days. Only full-follow-up weekly cohorts retained. |
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.FactMarket

Rows: 54,825. Key/grain: Date, CategoryKey, ChannelKey, RegionKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| PortfolioRevenue | float64 | No | Simulated focal portfolio net revenue in market grain; reconciles to FactSales. |
| CompetitorRevenue | float64 | No | Generated competitor dollar sales, nonnegative. |
| MarketRevenue | float64 | No | PortfolioRevenue + CompetitorRevenue; fictional share universe. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## fmcg.FactPromotion

Rows: 31,075. Key/grain: Date, ProductKey, CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| ProductKey | int64 | No | Stable conformed identifier. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| CustomerKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| CampaignKey | object | No | Product-account-week identifier. Campaign-year views split any campaign crossing calendar years. |
| ActualUnits | int64 | No | Simulated campaign-period units with promotion applied. |
| BaselineUnits | int64 | No | Known generator no-promotion units for the same SKU/account/day. Not a real causal estimate. |
| ActualRevenue | float64 | No | ActualUnits × discounted NetPrice, AUD. |
| BaselineRevenue | float64 | No | BaselineUnits × undiscounted same-period price, AUD. |
| ActualGP | float64 | No | Discounted campaign revenue − campaign COGS, AUD. |
| BaselineGP | float64 | No | BaselineUnits × (undiscounted price − unit cost), AUD. |
| TradeSpend | float64 | No | Campaign execution cost AUD. Does not include a second discount charge. |
| DiscountDepth | float64 | No | Fractional regular-price reduction. 0.12 = 12%. |
| IncrementalUnits | int64 | No | ActualUnits − BaselineUnits. |
| NetIncrementalProfit | float64 | No | ActualGP − BaselineGP − TradeSpend, AUD. |
## fmcg.FactSales

Rows: 248,580. Key/grain: Date, ProductKey, CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| ProductKey | int64 | No | Stable conformed identifier. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| CustomerKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| Units | int64 | No | Individual packs, integer. Not CCEP unit cases. |
| VolumeLitres | float64 | No | Units × product PackMl / 1000. |
| NetPrice | float64 | No | Realised net AUD per individual pack, after discount. |
| UnitCost | float64 | No | AUD variable cost per individual pack. |
| Revenue | float64 | No | Net sales AUD ex GST = Units × NetPrice. Discounts already included; excludes trade spend. |
| COGS | float64 | No | Variable simulated product cost AUD = Units × UnitCost. |
| GrossProfit | float64 | No | Revenue minus COGS, AUD; before trade spend/overheads. |
| PromotionFlag | int64 | No | 1 if this SKU/account/day participates in a simulated campaign. |
| DiscountDepth | float64 | No | Fractional regular-price reduction. 0.12 = 12%. |
| TradeSpend | float64 | No | Campaign execution cost AUD. Does not include a second discount charge. |
| Innovation | int64 | No | 0 existing SKU, 1 a simulated 2024 launch. |
## fmcg.FactTargets

Rows: 248,580. Key/grain: Date, ProductKey, CustomerKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| ProductKey | int64 | No | Stable conformed identifier. |
| CategoryKey | int64 | No | Stable conformed identifier. |
| CustomerKey | int64 | No | Stable conformed identifier. |
| ChannelKey | int64 | No | Stable conformed identifier. |
| RegionKey | int64 | No | Stable conformed identifier. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| TargetUnits | int64 | No | Planned units using assumed distribution and +6% 2024 baseline demand growth. |
| TargetRevenue | float64 | No | Independent pre-period planned AUD sales. Not actual × arbitrary post-hoc multiplier. |
## f1.DimCircuit

Rows: 24. Key/grain: CircuitKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| CircuitKey | object | No | Jolpica circuit ID. |
| Circuit | object | No | Public source descriptive attribute. |
| Country | object | No | Public source descriptive attribute. |
| Locality | object | No | Public source descriptive attribute. |
| Latitude | float64 | No | Public source descriptive attribute. |
| Longitude | float64 | No | Public source descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.DimConstructor

Rows: 12. Key/grain: ConstructorKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| Constructor | object | No | Public source descriptive attribute. |
| Nationality | object | No | Public source descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.DimDate

Rows: 731. Key/grain: Date.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| Year | int64 | No | Calendar attribute used for ordering/filtering; generated from Date. |
| YearMonth | object | No | Sortable YYYY-MM calendar month. |
| MonthNumber | int64 | No | Calendar attribute used for ordering/filtering; generated from Date. |
| Month | object | No | Calendar attribute used for ordering/filtering; generated from Date. |
| Quarter | object | No | Calendar attribute used for ordering/filtering; generated from Date. |
| WeekStart | object | No | Monday of week. Innovation cohort completeness counts from this date. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.DimDriver

Rows: 25. Key/grain: DriverKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| Driver | object | No | Public source descriptive attribute. |
| Nationality | object | No | Public source descriptive attribute. |
| DOB | object | No | Public driver date of birth. Not used for performance inference. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.DimRace

Rows: 46. Key/grain: RaceKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| Season | int64 | No | Completed F1 calendar season, 2023 or 2024. |
| Round | int64 | No | Race order within season, excluding cancelled events. |
| Race | object | No | Public source descriptive attribute. |
| CircuitKey | object | No | Jolpica circuit ID. |
| Date | object | No | Calendar day, ISO 8601; Power Query loads as date. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.DimSeason

Rows: 2. Key/grain: Season.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Season | int64 | No | Completed F1 calendar season, 2023 or 2024. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.FactConstructorStandings

Rows: 20. Key/grain: Season, ConstructorKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Season | int64 | No | Completed F1 calendar season, 2023 or 2024. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| Position | int64 | No | Official standings rank, or on-track lap position depending on table. |
| Points | float64 | No | Recorded session or final standings points; session scope determined by table. |
| Wins | int64 | No | Public source descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.FactDriverStandings

Rows: 46. Key/grain: Season, DriverKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Season | int64 | No | Completed F1 calendar season, 2023 or 2024. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| Position | int64 | No | Official standings rank, or on-track lap position depending on table. |
| Points | float64 | No | Recorded session or final standings points; session scope determined by table. |
| Wins | int64 | No | Public source descriptive attribute. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
## f1.FactLaps

Rows: 2,362. Key/grain: RaceKey, DriverKey, Lap.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| Lap | int64 | No | Source lap number. FactLaps grain includes driver and race. |
| Position | int64 | No | Official standings rank, or on-track lap position depending on table. |
| LapSeconds | float64 | No | Raw source driver-lap duration; includes traffic, interruptions and pit effects. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
## f1.FactPitStops

Rows: 1,737. Key/grain: RaceKey, DriverKey, Stop.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| Stop | int64 | No | Within-driver/race stop sequence integer. |
| Lap | int64 | No | Source lap number. FactLaps grain includes driver and race. |
| DurationSeconds | float64 | Yes | Source pit duration converted to seconds. One source null preserved; not stationary wheel-change time. |
| TimeOfDay | object | No | Source pit time-of-day string. No timezone inference. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| Laps | int64 | No | Completed driver race laps. Retirement may shorten denominator. |
| LapFraction | float64 | No | Pit lap / driver completed race laps. Not fraction of scheduled leader distance. |
| TimingEligible | int64 | No | 1 if recorded pit duration is between 10 and 60 seconds inclusive. Transparent screen; null/extremes remain in audit. |
## f1.FactQualifying

Rows: 919. Key/grain: RaceKey, DriverKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| QualifyingPosition | int64 | No | Ordinal qualifying-session result; differs from grid after penalties. |
| Q1Seconds | float64 | Yes | Q1 duration converted from timing string to seconds; null permitted if absent. |
| Q2Seconds | float64 | Yes | Q2 duration in seconds; null if not reached or not recorded. |
| Q3Seconds | float64 | Yes | Q3 duration in seconds; null if not reached or not recorded. |
## f1.FactRaceResults

Rows: 919. Key/grain: RaceKey, DriverKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| Grid | int64 | No | Official starting grid from source; 0 represents pit-lane start and is excluded from movement. |
| FinishPosition | int64 | No | Classified position assigned by source, including nonfinishers. Not necessarily completion order. |
| Points | float64 | No | Recorded session or final standings points; session scope determined by table. |
| Laps | int64 | No | Completed driver race laps. Retirement may shorten denominator. |
| Status | object | No | Source result status. Non-finish includes mechanical, accident, disqualification and other outcomes. |
| ClassifiedFinish | int64 | No | Derived 1 for current status Finished/Lapped or legacy +N Lap(s), else 0. Completion proxy, not FIA classification law. |
| PositionGain | float64 | Yes | Grid − FinishPosition when ClassifiedFinish=1 and Grid>0, otherwise null. |
## f1.FactSprintResults

Rows: 240. Key/grain: RaceKey, DriverKey.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| RaceKey | int64 | No | Season × 100 + round. Joins real race calendar. |
| DriverKey | object | No | Jolpica stable driver ID, not car number. |
| ConstructorKey | object | No | Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |
| Grid | int64 | No | Official starting grid from source; 0 represents pit-lane start and is excluded from movement. |
| FinishPosition | int64 | No | Classified position assigned by source, including nonfinishers. Not necessarily completion order. |
| Points | float64 | No | Recorded session or final standings points; session scope determined by table. |
| Laps | int64 | No | Completed driver race laps. Retirement may shorten denominator. |
| Status | object | No | Source result status. Non-finish includes mechanical, accident, disqualification and other outcomes. |
| ClassifiedFinish | int64 | No | Derived 1 for current status Finished/Lapped or legacy +N Lap(s), else 0. Completion proxy, not FIA classification law. |
| PositionGain | float64 | Yes | Grid − FinishPosition when ClassifiedFinish=1 and Grid>0, otherwise null. |
## public.PublicContext

Rows: 3. Key/grain: Metric.

| Field | CSV type | Missing allowed | Meaning |
|---|---|---|---|
| Metric | object | No | Public CCEP metric label; unique within disconnected context table. |
| Value | float64 | No | Fractional public growth value; basis/scope must accompany it. |
| Basis | object | No | Public release adjustment/comparability/FX basis. Do not mix with simulated nominal AUD growth. |
| Scope | object | No | Public corporate scope or fixed-snapshot analytical scope. |
| SourceURL | object | No | Attributed public source page. |
| PublishedDate | object | No | Source publication date, not date of simulated sales. |
| DataClass | object | No | Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED. |

## Derived outputs

The SQL definitions in `sql/transformations.sql` are authoritative for analytical fields. `ActionCentre` is a FY2024 fixed snapshot labelled SYNTHETIC_DERIVED. KPI formulas and filter guards are in `powerbi/dax_measures.md`. No public company value is joined into a synthetic fact.
