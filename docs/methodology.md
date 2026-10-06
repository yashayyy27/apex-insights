# Methodology and interpretation limits

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
