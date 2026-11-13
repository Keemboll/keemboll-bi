# Delta table checklist for Direct Lake

Stated **at the time of writing — check the current documentation**: [Understand Direct Lake query performance](https://learn.microsoft.com/fabric/fundamentals/direct-lake-understand-storage) and [Cross-workload table maintenance and optimization](https://learn.microsoft.com/fabric/fundamentals/table-maintenance-optimization).

The ETL code itself (Spark, T-SQL, pipelines) belongs to the data engineering team or to the Microsoft Fabric skills when installed. This checklist is what the semantic model needs from it.

## Table shape

- [ ] One Delta table per model table; star schema already built (`Fact_Sales`, `Dim_Customer`, `Dim_Product`, `Dim_Date`, `Dim_Store`).
- [ ] Integer surrogate keys (`CustomerKey`, `ProductKey`); same data type on both sides of each relationship; unique values on the one side, "Unknown" row (key −1) included.
- [ ] No complex Delta types, binary or GUID columns: convert them (GUID to string) upstream.
- [ ] No string longer than 32,764 characters; no `NaN` in floating point columns (limits at the time of writing).
- [ ] Only the columns the model needs; date and time split; numbers stored as numbers, not strings.
- [ ] Low cardinality where possible (rounded decimals, no free-text columns in facts).
- [ ] `Dim_Date` is a physical table, contiguous, one row per day.

## File layout

- [ ] **V-Order** enabled on the tables read by Direct Lake.
- [ ] **Few Parquet files, large row groups**: Microsoft's guidance is row groups of about 1 to 16 million rows; many small row groups mean many small segments and slower transcoding.
- [ ] File, row group and row counts of the largest table are below the [guardrails of the SKU](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview#fabric-capacity-requirements), with margin for growth. Record them in the design.
- [ ] Partitioning only on a **low-cardinality** column (Microsoft suggests fewer than 100–200 distinct values, for example a month rather than a date). Over-partitioning multiplies files and row groups.
- [ ] Delta Analyzer (semantic-link-labs, in a Fabric notebook) used to check row groups, files and V-Order when in doubt.

## Update patterns

- [ ] Prefer **append-only** loads for large facts: incremental framing keeps already loaded data in memory.
- [ ] Avoid **overwrite** of large tables: it forces a full cold reload.
- [ ] Deletes and updates on non-partitioned tables can rewrite most files: partition by a coarse column or accept the reload.
- [ ] Streaming or frequent small appends: schedule `OPTIMIZE` often enough to stay below the guardrails.

## Maintenance

- [ ] `OPTIMIZE` scheduled (consolidates small files). It rewrites files, so the next queries are cold: run it outside business hours.
- [ ] `VACUUM` retention **longer than the gap between two framings**: the framed version must still exist, otherwise queries fail on missing files. Reframe after the ETL, before the files are vacuumed.
- [ ] Maintenance automated (Lakehouse API, pipelines, notebooks) and monitored (`powerbi-operations`).

## Framing and ETL coordination

- [ ] Decide the refresh strategy with the ETL owner:
  - **Automatic updates on** (default at the time of writing): simplest; fine when each load leaves the tables consistent on its own.
  - **Automatic updates off + explicit reframe** at the end of the pipeline (REST API, TOM, schedule): when facts and dimensions load at different times and a report must never see new facts with old dimensions.
- [ ] Reframe **after** every table of the batch is committed; check that the reframe succeeded (refresh history, Direct Lake tab in the Fabric portal).
- [ ] If automatic updates stop after repeated failures, an on-demand refresh that succeeds resumes them (behaviour at the time of writing).
- [ ] Warm-up: after reframing, run the main report queries if first-query latency matters.
- [ ] Schema changes (renamed or removed columns) are picked up by a schema refresh in Desktop or web modeling, not by a scheduled refresh; renaming a source column removes the model column unless its source lineage is updated (see `powerbi-tmdl`).
