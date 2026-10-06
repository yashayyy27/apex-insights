# Power Query implementation

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
