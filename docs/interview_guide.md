# Interview defence guide

## 60-second explanation

“APEX INSIGHTS is a two-domain BI portfolio. The commercial domain uses
248,580 explicitly synthetic beverage sales records to analyse
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
Use Coffee: total +3.6%, existing range
-20.0%. Then use the 2,282
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
