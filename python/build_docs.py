"""Generate source-aligned documentation and an honest portfolio release status."""
import json
import pandas as pd
from common import ROOT,read_tables
from contracts import CONTRACTS,relationships
from measures import FMCG,F1
from build_powerbi import specs

def write(path,text):
    p=ROOT/path
    if path=='powerbi/runtime_acceptance.md' and p.exists() and '- [x]' in p.read_text().lower():
        print('Preserved recorded native acceptance evidence:',path)
        return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.strip()+'\n')

DEFINITIONS={
 'DataClass':'Row provenance. SYNTHETIC, PUBLIC or PUBLIC_DERIVED; analytical commercial extracts use SYNTHETIC_DERIVED.',
 'Date':'Calendar day, ISO 8601; Power Query loads as date.',
 'Revenue':'Net sales AUD ex GST = Units × NetPrice. Discounts already included; excludes trade spend.',
 'COGS':'Variable simulated product cost AUD = Units × UnitCost.',
 'GrossProfit':'Revenue minus COGS, AUD; before trade spend/overheads.',
 'NetPrice':'Realised net AUD per individual pack, after discount.',
 'UnitCost':'AUD variable cost per individual pack.',
 'Units':'Individual packs, integer. Not CCEP unit cases.',
 'VolumeLitres':'Units × product PackMl / 1000.',
 'PackMl':'Millilitres per individual pack.',
 'Innovation':'0 existing SKU, 1 a simulated 2024 launch.',
 'LaunchDate':'First sale eligibility. Products may not sell before this date.',
 'ActiveStoreDays':'One daily observation counts active stores for this SKU/account. Across dates/products, counts SKU-store-days, not distinct stores.',
 'EligibleStoreDays':'Eligible SKU-store-day exposure in the same grain/population.',
 'EligibleStores':'Fictional account store universe. Fixed for this scenario.',
 'TargetRevenue':'Independent pre-period planned AUD sales. Not actual × arbitrary post-hoc multiplier.',
 'TargetUnits':'Planned units using assumed distribution and +6% 2024 baseline demand growth.',
 'PromotionFlag':'1 if this SKU/account/day participates in a simulated campaign.',
 'CampaignKey':'Product-account-week identifier. Campaign-year views split any campaign crossing calendar years.',
 'BaselineUnits':'Known generator no-promotion units for the same SKU/account/day. Not a real causal estimate.',
 'ActualUnits':'Simulated campaign-period units with promotion applied.',
 'BaselineRevenue':'BaselineUnits × undiscounted same-period price, AUD.',
 'ActualRevenue':'ActualUnits × discounted NetPrice, AUD.',
 'BaselineGP':'BaselineUnits × (undiscounted price − unit cost), AUD.',
 'ActualGP':'Discounted campaign revenue − campaign COGS, AUD.',
 'TradeSpend':'Campaign execution cost AUD. Does not include a second discount charge.',
 'NetIncrementalProfit':'ActualGP − BaselineGP − TradeSpend, AUD.',
 'IncrementalUnits':'ActualUnits − BaselineUnits.',
 'DiscountDepth':'Fractional regular-price reduction. 0.12 = 12%.',
 'PortfolioRevenue':'Simulated focal portfolio net revenue in market grain; reconciles to FactSales.',
 'CompetitorRevenue':'Generated competitor dollar sales, nonnegative.',
 'MarketRevenue':'PortfolioRevenue + CompetitorRevenue; fictional share universe.',
 'Trials':'Distinct simulated trialists within each account/SKU/cohort; cohorts are independent.',
 'RepeatWithin28d':'Simulated trialists repeating within 28 days. Only full-follow-up weekly cohorts retained.',
 'RaceKey':'Season × 100 + round. Joins real race calendar.',
 'DriverKey':'Jolpica stable driver ID, not car number.',
 'ConstructorKey':'Jolpica constructor ID at this race. Team renames may have different IDs; not consolidated without policy.',
 'CircuitKey':'Jolpica circuit ID.',
 'Grid':'Official starting grid from source; 0 represents pit-lane start and is excluded from movement.',
 'FinishPosition':'Classified position assigned by source, including nonfinishers. Not necessarily completion order.',
 'Points':'Recorded session or final standings points; session scope determined by table.',
 'ClassifiedFinish':'Derived 1 for current status Finished/Lapped or legacy +N Lap(s), else 0. Completion proxy, not FIA classification law.',
 'PositionGain':'Grid − FinishPosition when ClassifiedFinish=1 and Grid>0, otherwise null.',
 'Status':'Source result status. Non-finish includes mechanical, accident, disqualification and other outcomes.',
 'Laps':'Completed driver race laps. Retirement may shorten denominator.',
 'QualifyingPosition':'Ordinal qualifying-session result; differs from grid after penalties.',
 'Q1Seconds':'Q1 duration converted from timing string to seconds; null permitted if absent.',
 'Q2Seconds':'Q2 duration in seconds; null if not reached or not recorded.',
 'Q3Seconds':'Q3 duration in seconds; null if not reached or not recorded.',
 'Stop':'Within-driver/race stop sequence integer.',
 'Lap':'Source lap number. FactLaps grain includes driver and race.',
 'DurationSeconds':'Source pit duration converted to seconds. One source null preserved; not stationary wheel-change time.',
 'TimeOfDay':'Source pit time-of-day string. No timezone inference.',
 'LapFraction':'Pit lap / driver completed race laps. Not fraction of scheduled leader distance.',
 'TimingEligible':'1 if recorded pit duration is between 10 and 60 seconds inclusive. Transparent screen; null/extremes remain in audit.',
 'LapSeconds':'Raw source driver-lap duration; includes traffic, interruptions and pit effects.',
 'Position':'Official standings rank, or on-track lap position depending on table.',
 'Metric':'Public CCEP metric label; unique within disconnected context table.',
 'Value':'Fractional public growth value; basis/scope must accompany it.',
 'Basis':'Public release adjustment/comparability/FX basis. Do not mix with simulated nominal AUD growth.',
 'Scope':'Public corporate scope or fixed-snapshot analytical scope.',
 'SourceURL':'Attributed public source page.',
 'PublishedDate':'Source publication date, not date of simulated sales.',
 'Season':'Completed F1 calendar season, 2023 or 2024.',
 'Round':'Race order within season, excluding cancelled events.',
 'DOB':'Public driver date of birth. Not used for performance inference.',
 'YearMonth':'Sortable YYYY-MM calendar month.',
 'WeekStart':'Monday of week. Innovation cohort completeness counts from this date.',
 'RegularPrice':'Base simulated pack price AUD before year/channel/promotion modifiers.',
}

def main():
    metrics=json.loads((ROOT/'outputs/insight_metrics.json').read_text())
    qa=json.loads((ROOT/'outputs/validation_report.json').read_text())
    pbi=json.loads((ROOT/'outputs/powerbi_source_validation.json').read_text())
    dictionary='# Data dictionary and grain contracts\n\nCommercial data is wholly SYNTHETIC; public context and F1 are separate. Every input field is listed. Row counts reflect this snapshot.\n\n'
    for domain in ['fmcg','f1','public']:
        for name,frame in read_tables(domain).items():
            contract=CONTRACTS[(domain,name)]
            dictionary+=f'## {domain}.{name}\n\nRows: {len(frame):,}. Key/grain: '+', '.join(contract['key'])+'.\n\n| Field | CSV type | Missing allowed | Meaning |\n|---|---|---|---|\n'
            for col in frame:
                meaning=DEFINITIONS.get(col,'Stable conformed identifier.' if col.endswith('Key') else 'Fictional descriptive attribute.' if domain=='fmcg' else 'Public source descriptive attribute.' if domain=='f1' else 'Attributed factual context.')
                if col in ['Month','MonthNumber','Year','Quarter']: meaning='Calendar attribute used for ordering/filtering; generated from Date.'
                dictionary+=f'| {col} | {frame[col].dtype} | '+('Yes' if col in contract['nullable'] else 'No')+' | '+meaning+' |\n'
    dictionary+='\n## Derived outputs\n\nThe SQL definitions in `sql/transformations.sql` are authoritative for analytical fields. `ActionCentre` is a FY2024 fixed snapshot labelled SYNTHETIC_DERIVED. KPI formulas and filter guards are in `powerbi/dax_measures.md`. No public company value is joined into a synthetic fact.\n'
    write('docs/data_dictionary.md',dictionary)
    write('docs/architecture.md','''# Architecture

```mermaid
flowchart LR
  A[CCEP attributed public facts] --> P[Disconnected PublicContext]
  B[Jolpica API cache + manifest] --> F[F1 normalization]
  C[Seeded fictional FMCG generator] --> S[Synthetic facts + dimensions]
  F --> Q[Contracts + validation]
  S --> Q
  Q --> D[Constrained SQLite mart]
  D --> V[Analytical SQL views]
  Q --> M[Power BI CSV partitions + M]
  M --> B1[Commercial PBIP + DAX]
  M --> B2[Motorsport PBIP + DAX]
  P --> B1
  V --> E[Formula-driven Excel pack]
  V --> I[Computed insights + action hypotheses]
  I --> B1
```

Two semantic models isolate domains and rights. Power BI is the principal
delivery format. Python performs source ingestion, seeded generation and
cross-table quality checks; M independently checks types, keys, provenance
and the product/category mapping before import. SQL enriches/aggregates each
fact independently, joining aggregates only at matching grain.

Daily FMCG fact keys are Date/Product/Customer. Date, Product, Category,
Customer, Channel and Region filter facts directly in one direction.
Category/channel/region keys are denormalized onto facts and tested against
product/customer attributes. This keeps the market denominator at its valid
category/channel/region grain without a many-to-many relationship.

F1 uses Race/Driver/Constructor facts. Season, Circuit and Date filter DimRace
then session facts. Final standings use Season with Driver or Constructor,
and intentionally do not react to race/circuit filters. There is no fact-to-fact
relationship, bidirectional filter, commercial/F1 union or invented tyre table.

Native PBIR pages and TMSL model.bim are version-control friendly. Windows
Power BI Desktop remains necessary for refresh, DAX runtime, interactions,
performance recording and actual Power BI screenshots. CSV/SQL evidence and
the Excel pack can be reviewed independently.
''')
    write('docs/methodology.md','''# Methodology and interpretation limits

## Provenance

`PUBLIC`: attributed CCEP Group extracts or unchanged F1 factual fields.
`PUBLIC_DERIVED`: normalized/joined F1 observations and calendar metadata.
`SYNTHETIC`: every fictional commercial input, including product names,
customers, costs, targets, distribution, market and panel fields.
`SYNTHETIC_DERIVED`: outputs computed from synthetic inputs.
`SIMULATION`: assumption-sensitive scenarios, always labelled in visuals.

Public CCEP growth is a disconnected context table with group scope and
comparable FX-neutral basis. It is not a prior for the generator, an Australian
market benchmark or evidence that the simulated revenue reflects CCEP.
See `docs/sources.md` for source URLs, rights and access decisions.

## Synthetic commercial design

Fixed seed 20261006, 24 fictional SKUs, five categories, 15 fictional accounts,
five channels, three Australian state regions, daily 2023–2024. No real retail
account names or Coca-Cola brand labels on transactional rows. All AUD figures
exclude GST. Unit means an individual beverage pack; litres use pack volume.

Category demand growth, seasonality, channel premiums, cost inflation,
distribution coverage and two launch ramps are explicit generator assumptions.
Multiplicative demand noise is shared between promoted and unpromoted potential
outcomes. Lift is therefore a **known simulated counterfactual**, not a real
observational causal estimate. It teaches the calculation, not identification.
Targets use independently planned distribution and a pre-period demand
expectation. They are not copied from realised sales.

## Grain and denominator discipline

- Revenue/units/cost add across daily SKU/account facts. Rates are ratios of sums.
- Distribution = active SKU-store-days / eligible SKU-store-days. Velocity =
  units / active SKU-store-days. These do not count distinct physical outlets.
- Market is one row per date/category/channel/region. Market dollars include
  focal dollars once plus generated competitor dollars. SKU/customer market
  share is undefined; DAX returns blank rather than an overstated numerator.
- Promotion evaluation uses promoted days only. Baseline and actual populations
  match. Net incremental profit = actual GP − baseline GP − trade spend. Net
  revenue already includes discounting, so there is no second discount expense.
- Revenue bridge at SKU/account grain: volume effect + realised price/mix effect
  + interaction + new-product effect = exact revenue change. It is an accounting
  decomposition, not a causal attribution. Pack and promotional mix can change ASP.
- Innovation repeat is repeats / trialists within independent weekly cohorts.
  Full 28-day follow-up after the end of the week is required. No summing
  overlapping person identities is claimed. Launch windows differ, so compare
  velocity/repeat and age rather than only cumulative sales.
- Distribution scenarios assume unchanged price/cost and specified velocity
  retention. Excel subtracts an explicit per-extra-store-day cost. Power BI
  revenue exposure excludes costs and is labelled accordingly.

## F1 interpretation

Two completed seasons, 46 races. Results and qualifying are separate: grid can
change after qualifying penalties. Championship totals include sprint results
and reconcile to official final standings. Progression named GP-only excludes
sprints. Constructor IDs at the race preserve team changes/renames.

Position gain is grid minus finish for status Finished/Lapped (legacy +N Lap(s)) and grid >0.
Source-classified nonfinishers are retained but excluded from that mean. Report
the eligible denominator and non-finish rate alongside movement to reveal
survivorship. `Non-finishes` includes accidents and DSQs, not only reliability.
Grid-points benchmark uses standard top-ten GP points. The difference is a
descriptive benchmark, not a claim that grid determines expected points.

Pit-duration strings are converted to seconds. One missing duration at 2024
British GP, Tsunoda stop 1, remains null. Timing comparisons use a transparent
10–60 second screen; excluded rows are retained. This is not stationary crew
service time. Comparisons are affected by circuit pit lanes, interruptions,
double-stacking and race context; SQL also provides a race-centred comparison.
Pit window = pit lap / driver completed race laps; retirement can distort it.

Only Bahrain and Monaco 2024 lap timings are sampled. No compound, stint or
weather table is invented. Raw laps include traffic, safety cars and pit effects;
no defensible tyre-degradation or undercut/overcut claim is made. Strategy Lab
uses balanced integer stints, assumed linear degradation reset on each stop
and constant assumed pit loss, all clearly SIMULATION. No outcome prediction.

## Evidence and deployment

Python/SQL are executed and validated. Excel formulas are recalculated and
perturbed in the artifact engine. Native Excel acceptance is recorded separately.
PBIR schemas and field bindings are checked. No DAX/M execution, Desktop
rendering, service publishing, RLS security or performance claim is established
without a Power BI runtime. Original code is MIT; F1 data/adaptations are
CC BY-NC-SA 4.0. No affiliation or commercial team outcome is implied.
''')
    write('powerbi/model_documentation.md','''# Semantic models

The two `model.bim` files include actual partitions, typed columns, relationships,
measure definitions, date marking metadata, lineage tags and disconnected
parameter tables. All keys are hidden; descriptive fields remain visible.
Import mode, en-AU query culture, compatibility level 1601. CSV partition paths
are relative to the single `DataRoot` M parameter.

## Commercial

Six conformed dimensions filter sales, distribution, targets, promotion and
innovation panel facts directly. Market has Date/Category/Channel/Region only.
Product carries Brand/PackMl/Innovation/LaunchDate rather than extra one-to-one
dimensions. Customer carries descriptive channel/region attributes but those
are not relationship chains; fact keys provide the conformed filters. Validators
enforce product/category and account/channel/region consistency.

`PublicContext` and the FY2024 `ActionCentre` snapshot are disconnected and
labelled. Action Centre has no ordinary analytical slicers; the snapshot scope
is displayed. `KPISelector`, `AnalysisAxis` field parameter and `DistributionGoal`
are disconnected. No target duplication through sales/promotion joins.

```mermaid
erDiagram
 DimDate ||--o{ FactSales : Date
 DimProduct ||--o{ FactSales : ProductKey
 DimCategory ||--o{ FactSales : CategoryKey
 DimCustomer ||--o{ FactSales : CustomerKey
 DimChannel ||--o{ FactSales : ChannelKey
 DimRegion ||--o{ FactSales : RegionKey
 DimDate ||--o{ FactMarket : Date
 DimCategory ||--o{ FactMarket : CategoryKey
 DimChannel ||--o{ FactMarket : ChannelKey
 DimRegion ||--o{ FactMarket : RegionKey
 DimProduct ||--o{ FactDistribution : ProductKey
 DimProduct ||--o{ FactTargets : ProductKey
 DimProduct ||--o{ FactPromotion : ProductKey
 DimProduct ||--o{ FactInnovationPanel : ProductKey
```

Diagram abbreviates repeated six-dimension relationships; `contracts.py` and
the model files are the complete relationship register.

## F1

Race/Driver/Constructor filter results, qualifying, sprint, pits and sample laps.
Date/Season/Circuit filter Race. Standings use Season+Driver or Season+Constructor
with explicit DAX guards for incompatible filters. No constructor attribute
on a career driver dimension: actual race team is retained in each fact.

```mermaid
erDiagram
 DimSeason ||--o{ DimRace : Season
 DimCircuit ||--o{ DimRace : CircuitKey
 DimDate ||--o{ DimRace : Date
 DimRace ||--o{ FactRaceResults : RaceKey
 DimDriver ||--o{ FactRaceResults : DriverKey
 DimConstructor ||--o{ FactRaceResults : ConstructorKey
 DimRace ||--o{ FactQualifying : RaceKey
 DimRace ||--o{ FactPitStops : RaceKey
 DimRace ||--o{ FactLaps : RaceKey
 DimSeason ||--o{ FactDriverStandings : Season
 DimDriver ||--o{ FactDriverStandings : DriverKey
 DimSeason ||--o{ FactConstructorStandings : Season
 DimConstructor ||--o{ FactConstructorStandings : ConstructorKey
```

No bidirectional or many-to-many relationship. No fabricated tyre/telemetry
dimension. Strategy parameters are independent assumptions, not fitted data.
''')
    write('powerbi/power_query.md','''# Power Query implementation

M functions and table queries are both in `model.bim` partitions and exported
under `power_query/`. This is executable source, not merely example prose.

`DataRoot`: set to the Windows checkout's `data/processed/` folder, with trailing
slash, once per model. No private file path is embedded in table queries.

`fnLoadCsv(relativePath,types,keyColumns,nullableColumns,permittedClasses)`:
UTF-8 CSV parser, promoted headers, exact schema check, trimmed strings, blank
to null, en-AU type coercion, required-null validation, grouped logical-key
duplicate detection and provenance validation. Invalid duplicates fail refresh;
they are not silently discarded, which would bias sales/points. Numeric nulls
only remain where the F1 source contract allows them (e.g. Q2/Q3 or missing pit timing).

`fnCalendar`: contiguous date sequence, typed date, year/month/quarter,
sortable YYYY-MM, Monday week start and provenance. No sparse fact-derived
date table. Date metadata is marked in the model.

`DimProduct`: meaningful nested join to DimCategory; fails unmatched or ambiguous
category keys and replaces the incoming descriptive category with canonical
mapping. Full referential integrity is additionally checked by Python/SQL before
import. M deliberately does not make a large fact-to-fact join.

No query-folding claim is made for flat-file import. In an enterprise warehouse,
move joins/filters into foldable SQL views, measure refresh duration and add
incremental refresh only after partition tests. Current data size is roughly
a quarter-million sales observations, not a benchmark of enterprise capacity.

Power Query runtime is pending Windows acceptance; schema validation of a
report does not parse/execute M.
''')
    spec_doc='# Dashboard specification and authored inventory\n\nNative pages exist in the PBIR report definitions. All runtime interactions are pending Windows verification.\n\n'
    for domain in ['fmcg','f1']:
        spec_doc+='## '+domain.upper()+'\n\n| Page | Decision question | Authored evidence |\n|---|---|---|\n'
        for title,question,kpis,charts in specs(domain):
            spec_doc+='| '+title+' | '+question+' | '+', '.join(t for _,t,_ in charts)+' |\n'
    spec_doc+='''

## Design system

1440×900 canvas, 208px navigation rail, 16px gutters, 108px KPI cards, two-by-two
analytical panels. Commercial: off-white/slate, restrained berry accent. F1:
navy/slate, mint accent. Segoe UI, direct titles, labelled units, sample sizes,
no affiliation logos, pies, 3D charts or decorative gauges. Standalone theme
JSON can be imported in Desktop; source visuals have explicit container/axis
formatting. Runtime accessibility/color/overflow review remains required.

## Interactions and honest scope

- Buttons navigate pages. `Executive view` bookmark restores the executive page
  without overwriting data selection; no invented presentation workflow.
- Category/channel/region or driver/constructor/race slicers have native sync
  groups. Default year/season 2024 is a report filter changed in Filters pane.
- Opportunity Finder has native decomposition-tree role bindings, a
  category/channel/region field parameter, KPI selector, dynamic title/format,
  and distribution What-If table. A revenue scenario is not a demand forecast.
- Native tooltip and drillthrough utility pages bind the real Product/Driver
  fields, not the field-parameter column. Use right-click drillthrough from a
  matching product/driver data point. Windows testing must confirm filter carry-over.
- Plan-gap chart uses a DAX color expression; tables display numeric context.
- Strategy Lab has four disconnected What-If tables. Added time is built from
  assumed stop loss plus triangular linear degradation across balanced integer
  stints. Stop-count selector interaction is disabled for the comparison
  curve/table so they retain all five alternatives while scenario cards change;
  other assumption controls still affect both. Native behavior requires testing.
  No grid/finish predictor is fabricated.
- Executive actions and public context are disconnected fixed-scope snapshots.
  They do not silently pretend to respond to analytical slicers.

`outputs/report_inventory.json` and `outputs/powerbi_source_validation.json`
record what exists and what was structurally checked. No `.pbix` binary or
actual Power BI screenshots are claimed before native runtime testing.
'''
    write('powerbi/dashboard_spec.md',spec_doc)
    write('powerbi/README.md','''# Power BI is the principal report delivery

Open `Commercial.pbip` and `Motorsport.pbip` in Windows Power BI Desktop.
These are native PBIR reports with TMSL semantic models, not a renamed ZIP
or placeholder PBIX. The CSV data is included in this snapshot. Use a current
Desktop version supporting PBIP/PBIR, as described in [Microsoft's project docs](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

1. Copy/clone the complete project onto Windows.
2. Open a `.pbip`. Transform data → Edit parameters → set `DataRoot` to the
   local `data/processed/` directory with trailing slash (e.g. `C:/APEX/apex-insights/data/processed/`).
3. Apply and refresh. Accept local file privacy settings appropriate to the
   public/synthetic data. Do not publish a stale model cache.
4. Import the optional matching `themes/*.json` through View → Themes. Report
   source already applies explicit container/axis formatting.
5. Run `DAXQueries/acceptance.dax` and compare to the SQL/Python evidence.
6. Execute `runtime_acceptance.md`, repair any native-runtime failures and
   save through Desktop. Record Desktop version and actual screenshots.

State: **authored source, schema/binding checked; native Power BI runtime pending**.
The macOS authoring environment cannot run Desktop. Source validation checks
file contracts and references; it does not certify DAX, M or UI behavior.
Do not claim completed deployed Power BI reports until acceptance is recorded.
''')
    write('powerbi/runtime_acceptance.md',f'''# Windows acceptance — pending

No boxes below are pre-marked. Record date, Desktop version, operator and evidence
under each item; update `outputs/powerbi_source_validation.json` only after an
actual native check, preserving source-validation results.

- [ ] Both PBIP files open with no model/visual errors.
- [ ] `DataRoot` updated once per semantic model; M applies and refreshes.
- [ ] FactSales has {metrics['sales_rows']:,} rows; date marking and relationships load.
- [ ] FY2024 Revenue = {metrics['revenue_2024']:,.2f}; GP margin = {metrics['gross_margin']:.10%}.
- [ ] Year filter 2023 yields the matching SQL control; LY is blank in first year.
- [ ] Clearing year selection blanks YoY/share-change metrics rather than comparing overlapping multi-year ranges.
- [ ] SKU/customer filtering makes simulated market share blank; category/channel/region share remains valid.
- [ ] Distribution and velocity reconcile to SKU-store-day denominators.
- [ ] Innovation page shows only launches, repeat cohorts respect cutoff.
- [ ] Final driver/constructor recorded points match official 2023 and 2024 standings.
- [ ] Race/circuit filters blank official final points; session points continue to respond.
- [ ] Teammate ahead/comparable counts reconcile to SQL under driver, race, constructor and season slices; shared-completion denominator remains visible.
- [ ] Null pit timing stays blank; eligible-stop counts exclude null/extreme durations.
- [ ] Navigation and Executive view bookmark work; bookmark preserves selections.
- [ ] Synced slicers preserve intended scope across pages; Action Centre snapshot stays labelled.
- [ ] Product/driver drillthrough carries selected context and tooltips show matching units/sample sizes.
- [ ] Decomposition tree and AnalysisAxis parameter switch correctly; mixed KPI formats remain correct.
- [ ] What-If controls change outputs; zero degradation gives stops × pit loss.
- [ ] Stop-count selection changes scenario cards; comparison curve/table retain all five alternatives via the authored NoFilter interaction.
- [ ] Formula-only simulation agrees with independent integer-stint calculation.
- [ ] All pages at 100% zoom pass overflow, contrast, keyboard and reading-order review.
- [ ] Performance Analyzer capture recorded; no speed benchmark claimed before capture.
- [ ] Export actual Power BI screenshots to `assets/screenshots/powerbi/`, with scope/data labels visible.
- [ ] Save `.pbix` if desired; keep binaries out of ordinary Git history or use Git LFS.

If an item fails, repair the source/runtime file and rerun affected checks. A
passing JSON schema is not a waiver for a failing native report.
''')
    write('docs/business_questions.md','''# Decision questions

## Commercial/category

1. Does revenue growth reflect litres, realised price/mix, new products or interactions?
2. Is a launch masking deterioration in the existing range?
3. Which category contributes the largest absolute change, not only the highest percentage?
4. Are channel target gaps explained by distribution exposure or store-level velocity?
5. Which high-margin products have distribution gaps worth testing?
6. Which SKUs need margin protection rather than extra listings?
7. Does promotion unit lift pay for lower realised prices and execution spend?
8. How sensitive is a distribution opportunity to velocity dilution and added cost?
9. Are launches meeting plan with sustainable cohort repeat, or merely initial trial?
10. What should a commercial manager test, and which KPI would invalidate the hypothesis?

## F1

1. How do GP-only progression and official final points differ once sprints are included?
2. Which drivers gain grid-to-finish positions with sufficient completed-race sample?
3. How does including all-cause non-finishes change that assessment?
4. Which constructors outperform a transparent starting-grid points benchmark?
5. Which teammates finish ahead most often in shared completed races?
6. Are circuit patterns supported by adequate starts, rather than single-race anecdotes?
7. Do pit-duration differences persist after centering within each race?
8. How much does the timing-outlier screen affect a pit comparison?
9. What strategy evidence is observable without compound/telemetry access?
10. How do hypothetical stop counts, pit loss and linear degradation assumptions trade off?

Each question maps to a native report page, a SQL view/query and/or a defined
measure. Questions requiring unavailable telemetry are not answered with
synthetic F1 facts.
''')
    write('docs/portfolio_case_study.md',f'''# APEX INSIGHTS — portfolio case study

## Problem

A category analyst needs to explain performance drivers and recommend tests,
not merely display revenue. A second domain tests whether the same discipline
holds for sports execution, where measurement populations and context differ.
The project targets the analytical thinking behind a CCEP Category Performance
& Insights role without pretending to have internal FMCG experience or access.

## Data

{metrics['sales_rows']:,} seeded daily fictional beverage sales records across
24 SKUs, 15 accounts, five categories/channels and three regions; independent
targets, distribution exposure, promotion counterfactuals and repeat cohorts.
CCEP Group public figures are disconnected context. Jolpica public 2023–2024
results, qualifying, sprints, standings and pits cover 46 races, with two sampled
2024 lap datasets. Rights/provenance are recorded at row and source levels.

## Analysis

Built a constrained SQLite mart, separate Power BI semantic-model sources,
{len(FMCG)+len(F1)} DAX measures, reusable Power Query functions, 16 PBIR page
definitions and a formula-driven Excel pack. Matched-grain joins avoid fanout.
An additive volume/price-mix/interaction/launch bridge reconciles exactly.
Quality checks reject wrong keys, mixed provenance, bad math and missing
required fields. F1 points reconcile including sprints.

## Insight

Synthetic 2024 revenue is AUD {metrics['revenue_2024']:,.0f}, up
{metrics['revenue_yoy']:.1%}. Coffee's total revenue grows
{metrics['weak_category_yoy']:.1%}, but existing Coffee SKUs decline
{abs(metrics['existing_coffee_yoy']):.1%}: launch revenue masks core weakness.
{metrics['negative_campaigns']:,} of {metrics['promo_campaigns']:,} FY2024
campaign-year records lift units while reducing net incremental profit.
In public F1 data, {metrics['top_mover']} averages
{metrics['top_mover_gain']:+.2f} classified position gain across
{metrics['top_mover_n']} eligible 2024 starts; the denominator and non-finishes
must accompany that result.

## Recommendation

Investigate existing-range exposure and demand before scaling the Coffee
launch. Test shallower discounts with a holdout and measure incremental GP
after execution costs. Prioritise selective distribution trials with velocity
retention and contribution gates. F1 conclusions remain descriptive: compare
pit timings within races, separate GP/sprint scope and expose survivorship.

## Business value

Demonstrates a repeatable path from business question to governed data,
driver analysis, action hypothesis and monitoring KPI. It provides an auditable
analytical framework, not realised corporate savings or an F1 strategy claim.
No causal real-world lift, deployed company dashboard or business impact is
invented. Power BI source files exist and pass structural checks; Windows
refresh/render/interaction acceptance is still required before claiming fully
tested native reports.
''')
    write('docs/interview_guide.md',f'''# Interview defence guide

## 60-second explanation

“APEX INSIGHTS is a two-domain BI portfolio. The commercial domain uses
{metrics['sales_rows']:,} explicitly synthetic beverage sales records to analyse
category growth, distribution, range economics, promotions and launches.
The F1 domain uses licensed public results for 2023–2024. I built the Python
pipelines, SQL mart, Power BI model/report source, DAX and Power Query logic,
and an Excel management pack. The strongest commercial finding is that a launch
can mask existing-range decline, and promotion volume lift can destroy profit.
Public facts and simulated data are separated throughout. Native Power BI
runtime acceptance is pending Windows access, so I distinguish source authoring
from tested execution.”

## Three-minute explanation

Start with the business problem: management asks what happened, where, why
and what to test. Explain why internal CCEP SKU/customer economics are unavailable
and how fictional names/row labels prevent misrepresentation. Describe the
daily star-schema grain and matched-grain market denominator. Explain that M
checks types/keys/provenance and Python/SQL test cross-table math and points.
Walk through revenue → category → product → channel → promotion → action.
Use Coffee: total +{metrics['weak_category_yoy']:.1%}, existing range
{metrics['existing_coffee_yoy']:.1%}. Then use the {metrics['negative_campaigns']:,}
negative-profit promotion records to explain why a volume KPI alone is weak.
Close with the distribution experiment and monitor contribution after added
cost, not hypothetical realised savings. Briefly contrast F1's public scope,
sprint reconciliation and completed-race selection bias. State what was run
locally and what awaits native Power BI testing.

## Technical explanation

Use `contracts.py` to demonstrate table keys and single-direction relationships.
Show `sql/transformations.sql`: aggregate separate facts before combining them.
Explain source JSON caching, 8-second rate limit, pagination and SHA-256 hashes.
Point to one DAX measure and one M partition in `model.bim`; these are actual
source definitions, not claims of deployed functionality. Show the Excel
scenario perturbation evidence and the corrupted-input tests.

## Commercial explanation

Category → brand → SKU → account → channel → performance → driver → opportunity
→ test → monitor. Distinguish volume growth from profit, distribution from
velocity, launch trial from repeat, gross margin from contribution after trade
spend, and opportunity exposure from a forecast. Listing cost/cannibalisation
could reverse a distribution business case.

## Power BI questions

- Why two models? Separate provenance/rights and incompatible business grains.
- Why import mode? Portable CSV snapshot; no DirectQuery or enterprise latency claim.
- Which interactions exist? Native page/button, bookmark, tooltip, drillthrough,
  sync-group, field-parameter and What-If definitions. Runtime status is pending,
  not a passing schema guarantee.
- How would you optimise? Measure with Performance Analyzer/DAX Studio first;
  reduce cardinality, push foldable work to SQL, test incremental refresh.
- RLS? Not implemented or claimed. Real customer security needs role design and tests.

## DAX questions

- CALCULATE changes filter context; DIVIDE handles zero denominator with blank.
- Gross margin is total GP / total revenue, not mean row margin.
- REMOVEFILTERS provides portfolio contribution; ALLSELECTED preserves chosen
  product universe. Explain the distinct business denominator before syntax.
- SAMEPERIODLASTYEAR/DATEADD require the contiguous date dimension; rolling
  sales use 28/91 calendar days, not 28/91 transaction rows.
- Why share blank under SKU/customer filters? Market has no such grain.
- Why official points blank under race filters? Final standings are season-grain.
- SWITCH/SELECTEDVALUE choose an explicit KPI, with a dynamic format expression.
- What-If simulation? Balanced integer stints and triangular degradation; no prediction.

## Power Query questions

- Why reject duplicates instead of keep first? Logical duplicates can bias totals
  and there is no evidence for which row is authoritative.
- How are nulls handled? Trim/blank-to-null, then type and contract checks.
  Genuine unavailable qualifying/pit timings stay null.
- Mapping? Product nested join to canonical category with one-match validation.
- Query folding? Flat files do not support the claimed warehouse folding path.
- Reuse? `fnLoadCsv`, `fnCalendar`, one `DataRoot` parameter per model.

## SQL questions

- Show CTE aggregation before fact joins and why it prevents fanout.
- Explain ROW_NUMBER versus DENSE_RANK; ties preserve different meanings.
- Why RANGE 27 PRECEDING on julianday? Calendar windows differ from transaction-row windows.
- Reconcile the revenue bridge and explain its price/mix interaction term.
- Teammates: join on race+constructor, different drivers, both completed; disclose selected population.
- Pit medians: rank within season/team, average central one/two observations.

## Data modelling questions

- State every fact's grain before proposing relationships.
- Product contains brand/pack attributes; extra one-to-one tables add no value.
- Customer/channel/region keys are checked against dimensional attributes.
- Market and standings cannot inherit arbitrary lower-grain filters.
- No fact-to-fact relationships or bidirectional filter shortcuts.

## Limitations and honest claims

Synthetic sales/market/cohort assumptions do not establish company performance.
Generator baseline is not a real causal effect estimate. F1 non-finishes are
all-cause; raw lap timings are not telemetry. Constructor renames are not
arbitrarily consolidated. Windows Power BI acceptance remains pending.
Use `docs/resume_bullets.md` and `docs/quality_gate.md`; do not add deployed
dashboards, enterprise throughput or realised savings to your resume.

## Challenges worth defending

The source had one null pit duration: retain it, explicitly exclude timing use.
Visual QA exposed a status-mapping error: the current API uses `Lapped`, while
legacy Ergast used `+N Lap(s)`. The transformation now accepts both, an
independent validation check catches corrupt completion flags, and regression
tests cover both status formats. This changed non-finish and movement scopes;
all affected SQL, report inputs and previews were regenerated.
Reconciling championship totals required sprint ingestion. A naive market join
would multiply denominators. Coffee's launch changed category interpretation.
Schema-validation issues were repaired but cannot stand in for Desktop QA.
Excel lookup/scenario calculations were perturbed rather than judged from
formula text alone.

## With real company data

Confirm grains, currency, returns, rebates, customer hierarchies and targets with
finance/category stakeholders. Add consented retailer scanner sell-out,
distribution/ACV, stock availability and promotional controls. Validate baseline
identification and cannibalisation, conduct holdout tests, include freight/listing
costs, apply RLS, test refresh SLAs and define an action owner/decision cadence.
Measure actual outcomes only after implementation and a valid comparison.
''')
    write('docs/resume_bullets.md',f'''# Resume bullets — current evidence only

- Built reproducible Python and SQL pipelines for {metrics['sales_rows']:,} labelled synthetic beverage sales records and two seasons of public F1 data, with constrained star schemas and automated data-quality checks.
- Authored native Power BI report/model source for 16 analytical pages, {len(FMCG)+len(F1)} DAX measures and reusable Power Query ETL, covering category economics, distribution, promotions and race execution; native runtime validation pending.
- Developed a formula-driven Excel management pack and commercial action hypotheses, identifying launch-masked core-range decline and {metrics['negative_campaigns']:,} simulated promotion records with volume lift but negative incremental profit.

Do not remove the Power BI validation qualifier until Windows acceptance is
complete. No employer data, deployed corporate dashboard, realised savings,
tyre telemetry or real company market-share claim is supported.
''')
    write('docs/quality_gate.md',f'''# Quality gate — candid self-review

These are subjective readiness assessments, not ratings from actual hiring
managers. Reviewer lenses were applied as a structured self-audit. Scores do
not override missing runtime evidence, and no score was rounded up to meet 90.

| Capability | Score /100 | Evidence and remaining gap |
|---|---:|---|
| Power BI sophistication | 72 | Native 16-page sources, parameters and utility pages; Desktop refresh/render/interaction testing missing |
| DAX | 84 | {len(FMCG)+len(F1)} source measures, meaningful denominators/filter guards; no Analysis Services execution/context tests |
| Power Query | 82 | Actual reusable functions, type/key/provenance and mapping logic; M refresh not executed |
| Data modelling | 93 | Explicit grains, one-direction relationships, market/standings guard design, constrained keys/FKs |
| SQL | 93 | CTEs, joins, windows, ranking, medians, exact bridge, time windows, executed mart |
| Commercial analytics | 92 | Promotion contribution, velocity/exposure, independent targets, launch-masked core decline, cost-sensitive Excel scenario |
| Category insights | 91 | Category-to-SKU/account logic, range segments and testable actions; no actual scanner/range evidence |
| Data storytelling | 91 | Observation-driver-action-monitor chain; denominator and simulated-impact distinctions visible |
| Documentation | 94 | Sources/rights, complete dictionary, reproduction, interview defence and acceptance status |
| Portfolio differentiation | 92 | Two distinct evidence domains and strong integrity discipline; native report QA still caps readiness |

## Hiring-manager lenses

**CCEP category/insights:** good evidence of commercial reasoning. Explicitly
fictional data avoids implying internal experience. Existing-range decline,
distribution/velocity and post-launch repeat are more relevant than decorative
KPIs. Native Power BI acceptance is necessary before treating the project as
strong proof of Desktop proficiency.

**Senior Power BI developer:** source work is substantive but not certified.
Inspect field-parameter metadata, filter propagation, tooltip/drillthrough scope,
M types, visual roles, DAX blank handling and performance in Desktop. Schema
pass is useful evidence, not runtime correctness.

**Business Analyst manager:** clear questions, constraints, test hypotheses,
monitoring KPIs and no invented delivery outcomes. Next step with stakeholders
would be scope/acceptance workshops and decision cadence.

**Commercial Insights manager:** promotion lift is not confused with profit,
launch growth does not erase core decline, and scenario costs are explicit.
Real baseline identification, cannibalisation and retailer economics remain absent.

**Technical recruiter:** repository provides runnable Python/SQL, a working
formula pack and native Power BI sources. Current resume wording must say
“authored source” and retain the runtime qualifier; screenshots labelled as
reference previews cannot serve as actual Power BI screenshots.

## Below-90 improvements already made

Added denominator guards, dynamic KPI formatting, stable lineage, integer-stint
simulation, native utility-page bindings, schema validation, independent controls
and Excel input perturbations. Further honest improvements to the three
sub-90 capabilities require Windows Power BI runtime evidence. See
`powerbi/runtime_acceptance.md`. Overall **native Power BI completion gate is
not yet passed**; this is not declared a fully certified finished dashboard project.
''')
    totalfacts=sum(len(frame) for domain in ['fmcg','f1'] for name,frame in read_tables(domain).items() if name.startswith('Fact'))
    write('README.md',f'''# APEX INSIGHTS

### Commercial & Performance Intelligence

A two-domain Business Intelligence portfolio: fictional FMCG category economics
and licensed public Formula 1 execution data. Designed around **question →
performance → driver → opportunity → action**, with Power BI as the principal
report format and Python, SQL and Excel providing reproducible evidence.

**Current release:** pipelines and analytical outputs implemented and tested;
native Power BI report/model source authored and structurally validated.
**Windows Power BI refresh/render/interaction acceptance remains pending.**
No deployed CCEP/F1 dashboard or realised company outcome is claimed.

## Project Overview

| Domain | Data | Analytical purpose |
|---|---|---|
| Commercial/category | {metrics['sales_rows']:,} **SYNTHETIC** daily sales rows; fictional brands/accounts | Growth, mix, range productivity, distribution, promotions, launch review and action hypotheses |
| F1 performance | **PUBLIC** 2023–2024 Jolpica results, qualifying, sprints, pits and standings; two sampled lap datasets | Championship scope, driver/team execution, circuit patterns, pit consistency and explicitly simulated strategy sensitivity |

{totalfacts:,} fact observations across the two models. All source files,
table grains, measures and checks can be inspected. The distinction between
public facts and generated performance is visible in rows, report footers,
Excel, documentation and the [source register](docs/sources.md).

## Why I Built This

To demonstrate commercial/category analytics and performance intelligence using
Power BI, DAX, Power Query, SQL, Python and Excel. The commercial domain is
relevant to the reasoning expected of a Category Performance & Insights Analyst:
category → brand → SKU → customer → channel → driver → test → monitor.
The F1 domain demonstrates a different discipline: separate qualifying/grid
scope, session points, race context and survivorship before drawing conclusions.
This project supports interview discussion; it does not imply employment,
affiliation or access to confidential Coca-Cola/CCEP information.

## Business Questions

- Is growth driven by volume, realised price/mix or launches?
- Does category growth hide declining existing-range performance?
- Where is a distribution gap attractive after velocity dilution and added cost?
- Which promotions lift packs but reduce contribution?
- Which launches combine repeat, velocity, margin and target attainment?
- Which drivers/constructors improve relative to grid, and how does non-finish
  selection alter that reading?
- How do sprint inclusion and pit-duration scope affect F1 conclusions?

Full decision map: [business questions](docs/business_questions.md).

## Architecture

```mermaid
flowchart LR
 A[Public CCEP facts] --> C[Disconnected context]
 B[Jolpica cache + hashes] --> F[F1 star model]
 S[Seeded fictional FMCG generator] --> M[Commercial star model]
 F --> Q[Contracts + validation]
 M --> Q
 Q --> SQL[SQLite analytical views]
 Q --> PBI[Power BI models + M + DAX]
 C --> PBI
 SQL --> X[Formula-driven Excel]
 SQL --> I[Insights + action hypotheses]
 I --> PBI
```

Detailed [architecture](docs/architecture.md), [methodology](docs/methodology.md)
and [data dictionary](docs/data_dictionary.md).

## Data Sources

**REAL PUBLIC DATA:** [CCEP's FY2024 public results](https://www.cocacolaep.com/news-and-stories/q4-and-fy-financial-results/)
provide three small attributed Group growth facts; they are not Australian
SKU/customer economics. Direct report download returned 403, so no restricted
scraping was performed. [Jolpica-F1](https://github.com/jolpica/jolpica-f1)
supplies the F1 snapshot via its documented API with cache, pagination,
custom User-Agent and conservative rate limiting.

The current public snapshot labels lapped finishers `Lapped`. Completion logic
accepts that status and legacy `+N Lap(s)`; it does not count lapped finishers
as retirements.

**SYNTHETIC DATA:** every commercial product/customer transaction, cost, target,
promotion, market denominator, distribution and cohort observation is generated.
All beverage brands and accounts are fictional. Synthetic share is share of
a generated market, never factual CCEP share. No public growth fact calibrates
the simulated operational model. [Source rights and attribution](docs/sources.md).

Code/original synthetic work is MIT. F1 data and adaptations are
**CC BY-NC-SA 4.0** under [Jolpica terms](https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md),
with [data attribution](data/LICENSE-F1.md). Third-party data is not relicensed as MIT.
Bundled Microsoft schemas retain their original notice; see
[third-party notices](THIRD_PARTY_NOTICES.md).

## Data Model

Commercial facts preserve daily SKU/account grain. Market has
date/category/channel/region grain; share goes blank for incompatible SKU/account
filters. Separate targets/distribution/promotion facts prevent fanout. Brands
and pack sizes live in Product; channel and region are conformed dimensions.

F1 facts use race/driver/team grain and actual race constructor assignments.
Final standings have season grain and filter guards. No invented tyre/telemetry
table, fact-to-fact or bidirectional relationship. [Model documentation](powerbi/model_documentation.md).

## Power BI

Native projects: [Commercial.pbip](powerbi/Commercial.pbip) and
[Motorsport.pbip](powerbi/Motorsport.pbip), with eight analytical pages each,
plus tooltip/drillthrough utility pages. They contain actual PBIR visual/query
bindings, semantic model partitions, **{len(FMCG)+len(F1)} DAX measure definitions**,
reusable M functions, field/What-If parameters, sync groups, navigation and an
executive bookmark. Source authored; runtime behavior is not yet certified.

Commercial pages: Executive, Category, Customer/Channel, Range, Promotion,
Innovation, Opportunity Finder and Action Centre. F1 pages: Championship,
Driver, Constructor, Circuit, Strategy Evidence, Pit Stops, Qualifying-to-Race
and Strategy Lab. The strategy evidence page transparently substitutes
observed pit windows for unavailable tyre-compound telemetry.

Read the [setup guide](powerbi/README.md), [page specification](powerbi/dashboard_spec.md),
[DAX library](powerbi/dax_measures.md), [M transformations](powerbi/power_query.md)
and [pending native acceptance checklist](powerbi/runtime_acceptance.md).

## Key Insights

**SYNTHETIC commercial findings, FY2024:**

- Revenue AUD **{metrics['revenue_2024']/1e6:.2f}M**, up **{metrics['revenue_yoy']:.1%}**; GP margin **{metrics['gross_margin']:.1%}** before trade spend/overheads.
- Coffee grows **{metrics['weak_category_yoy']:.1%}** overall, but existing Coffee SKUs decline **{abs(metrics['existing_coffee_yoy']):.1%}**. Launch revenue masks core-range weakness.
- **{metrics['negative_campaigns']:,} of {metrics['promo_campaigns']:,}** FY2024 campaign-year records lift units but reduce net incremental profit. The no-promotion baseline is a generator counterfactual.

**PUBLIC_DERIVED F1 findings:** {metrics['champion_constructor']} leads the
official 2024 constructor standings by **{metrics['constructor_points_gap']:.0f} points**.
Among drivers with at least ten eligible 2024 starts, {metrics['top_mover']}
has the highest average classified position gain (**{metrics['top_mover_gain']:+.2f}**,
**n={metrics['top_mover_n']}**). Nonfinishers/pit-lane starts are excluded from
movement, so this does not establish causal driver superiority.

All findings are computed by `python/analyse.py`, with SQL extracts and
[evidence-backed actions](docs/insights.md).

## Recommendations

Investigate existing-range Coffee demand/distribution before expanding the
launch. Test shallower discounts with matched controls and measure incremental
profit after execution costs. Trial selected high-margin distribution gaps,
using velocity retention and contribution after listing/logistics costs as
gates. These are hypotheses derived from synthetic analysis, with no realised
savings or real CCEP range recommendation claimed.

For F1, separate GP/sprint points, show movement sample/non-finishes and compare
pit duration within a race. The simulator explores assumptions; it does not
predict race outcomes or advise teams with unavailable telemetry.

## Technology

Power BI PBIP/PBIR + TMSL, DAX, Power Query M, Python pandas/NumPy/requests,
SQLite SQL, pytest/JSON Schema and a native `.xlsx` Excel pack with SUMIFS,
XLOOKUP, charts, conditional formatting and live scenario calculations.
PivotTables were not created; formula summaries give portable auditable behavior.

## Screenshots

The workbook previews are real rendered workbook outputs. The 16 data-derived
report reference layouts are Python renders, **not Power BI screenshots**.
Actual Power BI screenshots remain pending Windows runtime acceptance.
Open [the reference gallery](assets/preview.html) locally to browse every page.

![Commercial reference layout — synthetic data, not Power BI](assets/screenshots/reference/fmcg_01.png)

![F1 reference layout — public data, not Power BI](assets/screenshots/reference/f1_01.png)

![Excel category performance](excel/previews/Category_Performance.png)

## Reproducibility

Python 3.9–3.12. From this directory:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
python python/run_all.py
pytest -q tests
```

Default replay uses the included hashed public cache and needs no API network
access. `python python/run_all.py --refresh-public` fetches missing cache pages
under current source terms/rate limits; delete a chosen cache entry and manifest
entry only if intentionally replacing it. Existing cached pages are immutable.
`--refresh-public` permits API access, not automatic overwrite of the historical
snapshot. Pipeline saves manifests, validation, analytical extracts, insights
and report source, then renders the labelled reference gallery. It does not run
Power BI Desktop.
`python python/verify_reproducibility.py` replays offline and compares all
38 supplied processed CSVs byte-for-byte; its evidence is saved in
`outputs/reproducibility_report.json`.

Excel rebuild uses `node excel/build_management_pack.mjs` with the
`@oai/artifact-tool` dependency in a compatible authoring environment; the
exported workbook is supplied for ordinary Excel use. Python replay does not
require that proprietary authoring library. [Excel guide](excel/README.md).

## Validation

**{qa['checks']} data checks pass**, including keys/nulls/FKs, dates, sales/cost/GP
identities, store-day bounds, market components, cohorts, promotion profit,
championship points and raw hashes. **{pbi['schema_files_validated']} native
project/report files** pass Microsoft's JSON schemas; **{pbi['field_bindings_checked']}
field references** are checked. Adversarial tests inject duplicate keys, bad
math, wrong provenance and invalid dates. See [validation report](docs/validation_report.md).

Excel controls reconcile to Python; changing year and scenario inputs is tested
in the authoring engine. Source validation cannot certify DAX/M execution,
native report visual roles, interaction behavior or performance. The
[quality gate](docs/quality_gate.md) explicitly retains that gap.
Run `python python/audit_repository.py` to check the supplied export, links,
file sizes and processed hashes. See [repository audit](docs/repository_audit.md).

## Limitations

No internal CCEP data, genuine retailer market share, causal real-world promotion
effect, F1 compounds/weather/telemetry, enterprise-scale benchmark or realised
business outcome. Synthetic competitor dollars and category changes reflect
generator assumptions. One missing pit duration is retained. Sample raw lap
timings contain race confounders. Native Power BI runtime remains untested.
Detailed limitations: [methodology](docs/methodology.md).

## Future Improvements

Complete Windows acceptance and actual Power BI screenshots first. With lawful
access, add scanner sell-out/ACV, inventory/availability, real experimental
promotion baselines, costs/cannibalisation and governed customer security.
For F1, evaluate legitimate licensed compound/stint datasets before making
strategy-effect claims. Measure refresh/performance before scaling or deploying.

Recruiter materials: [case study](docs/portfolio_case_study.md),
[interview guide](docs/interview_guide.md), [defensible resume bullets](docs/resume_bullets.md).
''')
    print('Generated complete documentation and evidence-scoped resume bullets')

if __name__=='__main__': main()
