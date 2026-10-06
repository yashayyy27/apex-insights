# Dashboard specification and authored inventory

Native pages exist in the PBIR report definitions. All runtime interactions are pending Windows verification.

## FMCG

| Page | Decision question | Authored evidence |
|---|---|---|
| Executive Performance | What happened? | Revenue and plan by month, Category contribution, Plan gap by category, Performance and risks |
| Category Performance | Where is performance changing? | Category growth, Category trajectory, Brand and product economics, Volume growth |
| Customer and Channel | Where should commercial teams focus? | Channel net revenue, Distribution and velocity, Account performance, Regional plan gaps |
| Range and SKU Productivity | Which products deserve attention? | SKU economics: velocity vs margin, Product revenue, Range review evidence, Product plan gaps |
| Promotion and Pricing | Which promotions create profitable growth? | Net promotion profit by category, Discount depth vs net ROI, Lift and value tradeoffs, Promotion value through time |
| Innovation Performance | Which launches are working? | Launch trajectory, Launch reach and demand, Post-launch review, Repeat among complete trial cohorts |
| Opportunity Finder | Why did performance change? | Investigate the plan gap, Selected KPI by analysis axis, Distribution scenario candidates, Selected KPI |
| Executive Action Centre | What should we test next? | FY2024 generated action hypotheses; fixed snapshot scope, Public CCEP Group context; independent of simulation, Actions are hypotheses derived from synthetic data. No realised company outcomes. Refresh the Python pipeline to regenerate the FY2024 snapshot., Public CCEP Group growth is shown separately and does not validate fictional SKU/customer performance. |
## F1

| Page | Decision question | Authored evidence |
|---|---|---|
| Championship Command Centre | How did the championship develop? | Recorded driver points (GP + sprint), GP-only points progression, Official constructor points, Championship and execution |
| Driver Intelligence | Who converts opportunity into results? | Classified position gain, Qualifying and points per start, Driver comparison and sample sizes, Ahead of teammate; shared completed races |
| Constructor Performance | Where do points and non-finishes concentrate? | Constructor recorded points, All-cause non-finishes, Constructor execution, Driver points contribution |
| Circuit Intelligence | Where do observed results differ? | Observed position movement by circuit, Non-finishes by circuit, Circuit performance history, Circuit points concentration |
| Strategy Evidence | Observed pit windows; no compound telemetry | Recorded pit window by race, Sample raw lap times: Bahrain / Monaco 2024, Observed stop sequence, No tyre compounds, weather or telemetry supplied. Lap samples include traffic and interruptions. No degradation, undercut or clean-air-pace inference. |
| Pit Stop Performance | How consistent are recorded pit durations? | Eligible duration median by constructor, Duration dispersion, Audit all observed stops, Duration is the API pit-duration field, not stationary wheel-change time. Compare within a race. The 10–60 second screen retains excluded rows for audit. |
| Qualifying vs Race Execution | Who improves relative to their starting grid? | Grid vs finishing classification, Points above grid benchmark, Execution with survivorship context, Observed qualifying result |
| Strategy Lab | SIMULATION: explore assumption sensitivity | Added time across assumed stop counts, Simulation cost components, SIMULATION. Equal integer stints; linear assumed degradation reset by each stop; constant assumed pit loss. Excludes traffic, fuel, safety cars, compounds and overtaking., Outputs are extra elapsed-time assumptions relative to a constant fresh-tyre baseline. They are not race predictions or observed telemetry. |


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
