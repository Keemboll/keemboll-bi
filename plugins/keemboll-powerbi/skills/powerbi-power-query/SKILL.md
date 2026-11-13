---
name: powerbi-power-query
description: "Power Query (M) for Power BI semantic models: where a transformation belongs, query organisation and naming, parameters, query folding, column typing and data quality, error handling, incremental refresh, privacy levels and the formula firewall, refresh performance. Use to write, review or fix the M code of an Import or DirectQuery model, to diagnose a failing or slow refresh, to set up incremental refresh on a large fact table, or to decide whether a step should move upstream or stay in the model. Authoritative for M code; schema design stays in powerbi-data-modeling. Triggers: Power Query, M, M code, query folding, native query, incremental refresh, RangeStart, RangeEnd, parameters, staging query, data source, refresh, transform, ETL, dataflow, privacy levels, formula firewall, Table.Buffer, Value.NativeQuery, refresh failed, slow refresh, gateway."
---

# Power Query (M) — semantic models

Also apply `powerbi-conventions` (naming of model tables, approval before any change). This skill is authoritative for **M code**: other skills point here.

## When to use

- Writing, reviewing or fixing the M queries of an **Import** or **DirectQuery** model.
- A refresh that fails (type errors, firewall, credentials) or is slow.
- Setting up **incremental refresh** on a large fact table.
- Deciding where a transformation belongs.

Not for:

- Star schema, grain, keys, SCD → `powerbi-data-modeling`.
- Reading or writing partitions and `expressions.tmdl` in a PBIP project → `powerbi-tmdl` (this skill says *what* the M is, `powerbi-tmdl` says *where* it goes).
- Direct Lake models: no Power Query partitions → `powerbi-direct-lake`.
- Refresh scheduling, monitoring and alerts → `powerbi-operations`.
- DAX and report performance → `powerbi-performance`.

## Where does this transformation belong?

*As far upstream as possible, as far downstream as necessary* (Matthew Roche's maxim).

| Rank | Location | When |
|---|---|---|
| 1 | Source, or warehouse / lakehouse view or table | The rule is reusable beyond Power BI, the source is under the team's control |
| 2 | Dataflow or upstream pipeline | Shared by several semantic models; avoids copying the same M into each model |
| 3 | Power Query in the model | Specific to this model; must fold, or the volume is small |
| 4 | DAX calculated column | Last resort: needs model context (e.g. `RELATED`), or no access upstream |

Record each "stays in the model" decision with its reason when the rule could move upstream later (`DEBT.md`, see `powerbi-lean`).

## Rules

### Organisation and naming (defaults)

- **Staging queries** prefixed `stg_` (`stg_Sales`), **load disabled**; loaded queries reference them.
- **Loaded queries** named exactly as the model table (`Fact_Sales`, `Dim_Customer`).
- **Parameters** prefixed `p` (`pServer`, `pDatabase`) or grouped in a `Parameters` group — `RangeStart` / `RangeEnd` keep their reserved names.
- **Functions** prefixed `fn` (`fnCleanKey`), with documentation metadata.
- **Query groups** by default: `Parameters`, `Functions`, `Staging`, `Dimensions`, `Facts`.
- **One step = one intention**, with a meaningful name (`#"Kept order columns"`, never `#"Changed Type1"`). A comment (`//`) on every non-obvious step says *why*.

### Parameters

- Server, database, path, environment: **always** parameters, never hard-coded in a source step. In a PBIP project they live in `expressions.tmdl` (`powerbi-tmdl`).
- Values are switched per environment at deployment (`powerbi-alm`).
- **Never** a secret in a parameter or in M: credentials live in the service data source settings or the gateway.

### Query folding

Details, step list and diagnostics: [references/query-folding.md](references/query-folding.md).

- Folding = the engine translates steps into the source's native query. Unfolded steps run in the mashup engine, after all rows came over the network.
- **Verify, do not assume**: folding depends on the connector, its version and the exact step. Check with *View Native Query*, the step folding indicators (Power Query Online) or *Query diagnostics*.
- **Order**: filter rows and remove columns first, non-foldable steps last.
- Native SQL when unavoidable: `Value.NativeQuery ( ..., [EnableFolding = true] )` for connectors that support it.

### Typing and data quality

- **Explicit types on every column, once**, at the end of staging. Text → date/number conversions pass a **culture** (`Table.TransformColumnTypes ( ..., "en-US" )`).
- Money as **fixed decimal** (`Currency.Type`), keys as **whole numbers** (`Int64.Type`), no `any` column loaded.
- Split date and time; trim and clean text keys; handle nulls explicitly (replace, keep, or route to the Unknown member as decided in `powerbi-data-modeling`).
- `try ... otherwise` **only** when the fallback is a decided business rule — never to hide errors. Count rejected rows in a non-loaded query that tests can read (`powerbi-testing`).

### Incremental refresh

Full procedure and pitfalls: [references/incremental-refresh.md](references/incremental-refresh.md).

- Parameters named exactly `RangeStart` and `RangeEnd`, type **Date/Time**.
- Filter `[OrderDate] >= RangeStart and [OrderDate] < RangeEnd` — one inclusive bound only, otherwise duplicates.
- The filter **must fold**, otherwise every partition reads the whole table.
- Default policy: archive 5 years, refresh the last 10 days.

### Privacy levels and gateway

- The **formula firewall** blocks combining sources whose privacy levels differ (`Formula.Firewall` errors). Fix it by restructuring (one query per source, combine in a separate query) or by setting correct levels — not by *Ignore privacy levels*, which is a Desktop file option and does not describe how the service evaluates the published model.
- On-premises sources need a **gateway**; cloud and on-premises sources mixed in one query have gateway consequences: check the current Microsoft documentation before designing that.
- Native queries may require user approval in Desktop; do not disable the prompt globally to get rid of it.

### Refresh performance

- Reduce columns and rows at the first steps; disable load of every helper query.
- A query referenced by several others may be **evaluated once per reference**: do not branch a heavy query many times without measuring.
- `Table.Buffer` is not a reflex: it breaks folding and holds the table in memory. Use it only for a measured gain (e.g. a small lookup list read many times).
- Refresh parallelism limits depend on the source, the gateway and the capacity: measure, and point to the Microsoft documentation for current limits.

## Process

1. **Read** the existing M (`powerbi-tmdl` for a PBIP project): sources, parameters, staging chain, loaded tables.
2. **Check folding** step by step on the heavy queries; note where it stops.
3. **Propose** the changes as a query / step / change / reason table, with expected impact on refresh time.
4. **Wait for approval** (`powerbi-conventions`), especially for anything that changes a loaded column's name or type.
5. **Apply** through `powerbi-tmdl`.
6. **Refresh and reconcile** row counts and totals with the source (`powerbi-testing`); record refresh time before / after.

Review checklist: [references/review-checklist.md](references/review-checklist.md).

## References

- [references/m-patterns.md](references/m-patterns.md) — parameterised SQL source, incremental fact query, date dimension, staging + reference, documented function, safe type conversion, folder combine.
- [references/query-folding.md](references/query-folding.md) — folding checks and the steps that break it.
- [references/incremental-refresh.md](references/incremental-refresh.md) — procedure, policy decisions, pitfalls.
- [references/review-checklist.md](references/review-checklist.md) — the checklist.
