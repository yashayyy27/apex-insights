# APEX INSIGHTS — portfolio case study

## Problem

A category analyst needs to explain performance drivers and recommend tests,
not merely display revenue. A second domain tests whether the same discipline
holds for sports execution, where measurement populations and context differ.
The project targets the analytical thinking behind a CCEP Category Performance
& Insights role without pretending to have internal FMCG experience or access.

## Data

248,580 seeded daily fictional beverage sales records across
24 SKUs, 15 accounts, five categories/channels and three regions; independent
targets, distribution exposure, promotion counterfactuals and repeat cohorts.
CCEP Group public figures are disconnected context. Jolpica public 2023–2024
results, qualifying, sprints, standings and pits cover 46 races, with two sampled
2024 lap datasets. Rights/provenance are recorded at row and source levels.

## Analysis

Built a constrained SQLite mart, separate Power BI semantic-model sources,
78 DAX measures, reusable Power Query functions, 16 PBIR page
definitions and a formula-driven Excel pack. Matched-grain joins avoid fanout.
An additive volume/price-mix/interaction/launch bridge reconciles exactly.
Quality checks reject wrong keys, mixed provenance, bad math and missing
required fields. F1 points reconcile including sprints.

## Insight

Synthetic 2024 revenue is AUD 87,719,379, up
13.7%. Coffee's total revenue grows
3.6%, but existing Coffee SKUs decline
20.0%: launch revenue masks core weakness.
2,282 of 2,321 FY2024
campaign-year records lift units while reducing net incremental profit.
In public F1 data, Lewis Hamilton averages
+2.50 classified position gain across
22 eligible 2024 starts; the denominator and non-finishes
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
