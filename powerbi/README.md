# Power BI is the principal report delivery

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
