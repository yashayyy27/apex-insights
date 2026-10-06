# Windows acceptance — pending

No boxes below are pre-marked. Record date, Desktop version, operator and evidence
under each item; update `outputs/powerbi_source_validation.json` only after an
actual native check, preserving source-validation results.

- [ ] Both PBIP files open with no model/visual errors.
- [ ] `DataRoot` updated once per semantic model; M applies and refreshes.
- [ ] FactSales has 248,580 rows; date marking and relationships load.
- [ ] FY2024 Revenue = 87,719,379.47; GP margin = 48.6888194924%.
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
