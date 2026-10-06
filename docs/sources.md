# Source register

Research cut-off: 6 October 2026. Historical analytical scope is deliberate:
completed 2023–2024 seasons and a matching simulated commercial calendar.

| Source | Use | Access and rights | Separation |
|---|---|---|---|
| [CCEP FY2024 results, published 14 February 2025](https://www.cocacolaep.com/news-and-stories/q4-and-fy-financial-results/) | Public Group revenue growth 3.5%, operating profit growth 8.0%, EPS growth 6.5%; all adjusted/comparable FX-neutral as labelled | Small attributed factual extracts manually curated from public indexed release. Direct download returned 403; no restricted scraping attempted | Disconnected `PublicContext` table, never used to calibrate simulated customer sales |
| [CCEP annual reports](https://ir.cocacolaep.com/financial-reports-and-results/annual-reports) | Context/reference for business framing | Linked only; copyrighted report not redistributed | No inferred private performance |
| [Jolpica documentation](https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md) | Race results, qualifying, sprints, pit stops, official final driver/constructor standings; sample laps | Documented API, custom User-Agent, limit 100, cached paginated responses | PUBLIC / PUBLIC_DERIVED |
| [Jolpica terms](https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md) | Licence | Data CC BY-NC-SA 4.0; not Apache licence of API software | See `data/LICENSE-F1.md` |
| [Jolpica rate limits](https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md) | Ingestion control | 4 requests/sec and 500/hour; this client uses >=8 sec and honors Retry-After | Cache-first and bounded retry |
| Project generator | Fictional beverage products, customers, channels, regions, prices, costs, targets, distribution, promotions, market benchmark and panel repeat | Original synthetic data, fixed seed | Every row `SYNTHETIC`; every commercial result `SYNTHETIC_DERIVED` |
| [Microsoft PBIR documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-report) | Native report authoring | Public JSON schemas; schema snapshots retained | Source validation does not establish Desktop runtime behavior |
| [Microsoft semantic model documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset) | PBIP / TMSL model.bim authoring | Public format | No invented Power BI execution claims |

No Coca-Cola or F1 logos are used. All simulated beverage brands are fictional.
Grocery, convenience, petrol, hospitality and independent retail are channel
concepts; the customer names identify fictional accounts, not real retailers.
No telemetry, compounds, weather, scanner market share or confidential CCEP
customer information is included. Synthetic share means share of a generated
market denominator; it is never a company or industry fact.
