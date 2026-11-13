---
name: powerbi-performance
description: "Power BI performance optimization: DAX code (anti-patterns, variables, filters, iterators), model size and cardinality (VertiPaq), Power Query (query folding, incremental refresh), Direct Lake / DirectQuery, slow reports and diagnostic method (Performance analyzer, DAX Studio, Best Practice Analyzer). Use to audit or speed up a slow model, measure or report page, or to review DAX / M before going to production. Triggers: performance, optimization, optimize, slow, fast, speed up, VertiPaq, cardinality, model size, query folding, refresh, incremental refresh, DAX Studio, Performance analyzer, Server Timings, best practice."
---

# Performance — DAX, model, reports

Also apply `powerbi-conventions`. Structural fixes are covered by `powerbi-data-modeling`; writing TMDL by `powerbi-tmdl`; M code and incremental refresh by `powerbi-power-query`; anything about Direct Lake by `powerbi-direct-lake`.

## Diagnostic method (always measure before optimizing)

1. **Locate**: which page / which visual is slow? (Power BI Desktop → *Performance analyzer*, note the *DAX query* duration vs *Visual display*.)
2. **Isolate** the DAX query of the visual (copy it from Performance analyzer) and run it in DAX Studio with *Server Timings*: **Formula Engine** (FE) time vs **Storage Engine** (SE) time, number of SE queries.
   - FE dominant → DAX to rewrite (iterations, context).
   - SE dominant / many queries → model (cardinality, relationships) or filters.
3. **Model size**: DAX Studio → *View Metrics* (VertiPaq Analyzer): heaviest columns, cardinalities, relationship sizes.
4. **Automatic rules**: Tabular Editor → *Best Practice Analyzer*.
5. **Fix one thing at a time** and measure again; record before / after in a table.

Never present an optimization as achieved without a before / after measurement.

## DAX — priority rules

| Avoid | Prefer | Why |
|---|---|---|
| `CALCULATE ( [M], FILTER ( Fact, Fact[Col] = "x" ) )` | `CALCULATE ( [M], Fact[Col] = "x" )` | Column filter pushed to the SE, no iteration of the table |
| Same sub-expression repeated | `VAR` | Evaluated only once |
| `IFERROR ( a / b, 0 )` | `DIVIDE ( a, b )` | No costly error handling |
| `SUMX ( Fact, Fact[Q] * RELATED ( Dim[Price] ) )` over hundreds of millions of rows | Column computed upstream (source / Power Query) | Iteration + RELATED per row |
| Nested iterators (`SUMX` inside `SUMX`) over large tables | Aggregate first at the right grain (`SUMMARIZE`/`VALUES` + `SUMX`) | Reduces the number of rows iterated |
| `COUNTROWS ( FILTER ( … ) ) > 0` | `NOT ISEMPTY ( CALCULATETABLE ( … ) )` | Stops at the first result |
| `ALL ( Fact )` | `REMOVEFILTERS ( Dim[Col] )` or `ALL` on targeted columns | Less data materialized |
| `FORMAT` / concatenations in numeric measures | Format strings (dynamic if needed) | Text = no cache, broken sorting |
| `IF` that returns 0 instead of BLANK | Leave `BLANK()` | Zeros densify visuals (every combination) |
| `DISTINCTCOUNT` measures on a very high-cardinality column | Pre-aggregate or approximate (`APPROXIMATEDISTINCTCOUNT` in DirectQuery) | Memory / CPU cost |

Detailed before / after examples: [references/dax-anti-patterns.md](references/dax-anti-patterns.md).

## Model — priority rules

- **Remove** unneeded columns and rows (out-of-scope history, unused technical columns).
- **Reduce cardinality**: split date and time, round decimals, drop seconds, replace GUIDs / long text with integer keys.
- **Types**: integers for keys, fixed `decimal` rather than `double` for amounts.
- **Turn off** Auto date/time (it creates a hidden table per date column).
- **Relationships**: 1→\*, single-direction, on integer columns; avoid bidirectional and `*:*`.
- **Calculated columns** → move to Power Query or to the source.
- **High cardinalities on facts** (line number, timestamp): do not load them when unused.

Details and thresholds: [references/power-query-template.md](references/power-query-template.md).

## Power Query

`powerbi-power-query` is authoritative for M code and incremental refresh; the points below are only the performance summary.

- Check **query folding** (right-click the step → *View native query*); place non-foldable steps as late as possible.
- Filter rows and remove columns **first**.
- **Incremental refresh** on large fact tables (`RangeStart` / `RangeEnd` parameters).
- No merges between different sources when avoidable (it prevents folding).

## Reports

- Default: at most 8 visuals per page (house heuristic, not a Microsoft rule); group KPIs into a single multi-row card visual when possible.
- Limit synced slicers and unneeded interactions (*Edit interactions*).
- Avoid tables / matrices with tens of thousands of visible rows.
- Report page tooltips: keep them light (they run their own queries).
- Custom visuals: check their cost in Performance analyzer.
- *Query reduction* option (Apply button on slicers) for DirectQuery models.

## Audit deliverable

| # | Object | Finding | Measure before | Fix | Measure after | Gain |
|---|---|---|---|---|---|---|
