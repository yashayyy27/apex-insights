# Native Excel acceptance

Status: **NOT VERIFIED**. A native Microsoft Excel UI session was attempted,
but computer-use access timed out before the workbook could be opened or tested.
No native-app recalculation/export claim is made.

The artifact authoring engine successfully recalculates the workbook, checks
revenue/margin against Python, changes year and velocity retention, tests zero
distribution expansion, renders all nine sheets and exports the XLSX. Evidence:
`verification.json` and `previews/`. All visible sheets were inspected.

For native acceptance, open the supplied workbook in Microsoft Excel and verify:

- No repair, unsupported function or external-link warnings.
- Executive revenue AUD 87,719,379.47 and margin 48.68881949% for 2024.
- Year 2023 switches executive/category/account summaries; action/launch/SKU
  snapshots retain their explicit FY2024 labels.
- Scenario SKU lookup finds unique source key; retention 80% lowers incremental
  contribution while baseline sales remain unchanged.
- Distribution target below baseline creates zero expansion and contribution.
- Charts and conditional formatting update after relevant input changes.
- Save/reopen preserves formulas, source tables, styles and selected controls.

Record actual version/date/evidence before changing status. Do not interpret
XLSX export success as native Excel certification.
