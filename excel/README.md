# Commercial management pack

Open `management_pack.xlsx` in Excel. All performance data is **SYNTHETIC**,
AUD ex GST. Nine populated sheets: Executive Summary, Category Performance,
Customer Channel, Innovation, Scenario Analysis, three source tabs and Methodology.

Change the reporting year on Executive Summary (2023/2024); monthly, category
and account summaries recalculate through bounded SUMIFS. Scenario Analysis
uses exact-match XLOOKUP to retrieve FY2024 SKU inputs, then calculates extra
active store-days, units, revenue, GP and contribution after added cost.
The amber assumptions are editable; FY2024 action/launch/SKU snapshots keep
their explicitly stated scope regardless of the year control.

Three native charts, conditional plan/scenario formatting, named source tables,
validation and freeze panes support review. No decorative PivotTable claim is
made: bounded formula summaries were chosen for reliable portable exports.
Source aggregates are traceable to executed SQL views, not manually invented KPIs.

`verification.json` records recalculation, independent revenue/margin controls,
year switch, velocity-retention perturbation, zero expansion boundary and error
scan. `previews/` contains rendered worksheet evidence. Native Excel app checks
are recorded separately in `native_acceptance.md` when actually performed.

Authoring: `build_management_pack.mjs` uses `@oai/artifact-tool` in the bundled
Codex artifact environment. The workbook itself opens in ordinary Excel without
that library. Rebuild inputs with Python, then rebuild with the compatible
artifact engine. Rebuilding the Python pipeline alone does not refresh a saved XLSX.
