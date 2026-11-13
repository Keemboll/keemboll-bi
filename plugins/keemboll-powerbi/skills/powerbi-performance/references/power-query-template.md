# Model and Power Query — details

## VertiPaq pointers

- The size of a column depends mostly on its **cardinality** (number of distinct values), not on the number of rows.
- Warning signs in VertiPaq Analyzer:
  - a column > 10–20 % of the model size;
  - a `DateTime` column with hours / minutes / seconds on a fact table;
  - long text keys or GUIDs;
  - hidden `LocalDateTable_…` tables (Auto date/time turned on);
  - relationships whose size exceeds that of the columns.

## Reducing cardinality

| Column | Action |
|---|---|
| Timestamp | Split into `Date` (date) and `Time` (rounded to the quarter hour, or removed) |
| Amount with 6 decimals | Round to 2 decimals, fixed decimal type |
| Text identifier | Integer surrogate key, text kept in the dimension |
| Free-text comment | Do not load, or put in a separate detail table in DirectQuery |

## Query folding

`powerbi-power-query` is authoritative for M code; this section only lists what matters for performance.

- Sources that fold: SQL Server, Fabric Warehouse / SQL endpoint, Synapse, Oracle, PostgreSQL, OData partially.
- Steps that often break folding: `Table.Buffer`, adding an index, merging with another source, some custom text functions.
- Check: right-click → *View native query* (greyed out = no folding), or the step folding indicators in Power Query Online.

## Incremental refresh

`powerbi-power-query` is authoritative for incremental refresh; summary:

1. Create the `RangeStart` and `RangeEnd` parameters (Date/Time type, sample values).
2. Filter the table: `each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd` (strict inequality on one side to avoid duplicates).
3. Check that the filter **folds** to the source.
4. Define the policy. Default: archive 5 years, refresh the last 10 days.

## Direct Lake (Fabric)

`powerbi-direct-lake` is authoritative for Direct Lake; summary of the performance points:

- Optimize the Delta tables: V-Order, `OPTIMIZE`, reasonable file size, few small files.
- Prefer **Direct Lake on OneLake** for new models: no DirectQuery fallback, no dependency on the SQL analytics endpoint.
- Avoid non-materialized SQL views: on OneLake they are not supported; on the SQL analytics endpoint they cause a DirectQuery fallback. Materialize the view as a Delta table.
- Watch the capacity guardrails (Parquet files, row groups, rows): on the SQL analytics endpoint, exceeding them causes a DirectQuery fallback (`DirectLakeBehavior` property); on OneLake, the query fails (visuals do not render).
- Fallback on the SQL analytics endpoint: `EVALUATE TABLETRAITS ()` gives the cause per table in the `DirectLakeFallbackInfo` column (`None` = Direct Lake).

## DirectQuery

- Indexes / statistics on the source side, pre-aggregated views.
- Aggregation tables in Import (*Manage aggregations* feature).
- Dimensions in **Dual** mode.
- Limit visuals per page and turn on query reduction.
