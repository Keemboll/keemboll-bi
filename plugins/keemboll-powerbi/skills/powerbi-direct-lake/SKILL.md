---
name: powerbi-direct-lake
description: "Design and run Power BI semantic models in Direct Lake storage mode on Microsoft Fabric (Delta tables in OneLake), and choose between Import, Direct Lake on OneLake, Direct Lake on SQL analytics endpoint, DirectQuery and composite models. Use when deciding the storage mode of a new model, building a model on a lakehouse or warehouse gold layer, preparing Delta tables for Direct Lake, controlling framing and refresh during ETL, diagnosing DirectQuery fallback or guardrail errors, placing RLS/OLS (semantic model, OneLake security, SQL endpoint), or migrating an Import model to Direct Lake. Triggers: Direct Lake, DirectLake, OneLake, Fabric, lakehouse, warehouse, Delta, Parquet, V-Order, OPTIMIZE, VACUUM, framing, reframe, transcoding, cold query, fallback, DirectQuery fallback, DirectLakeBehavior, TABLETRAITS, guardrails, capacity SKU, storage mode, Import vs Direct Lake, composite model, SQL analytics endpoint, OneLake security, fixed identity, gold layer, medallion."
---

# Direct Lake — Power BI on Fabric

Direct Lake moves fast. Every limit or preview status below is stated **at the time of writing — check the current documentation** before relying on it: [Direct Lake overview](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview) (comparison tables, guardrails, considerations and limitations).

Also apply `powerbi-conventions` (naming, approval). This skill is authoritative for Direct Lake; the short storage-mode table in `powerbi-data-modeling` summarizes it.

## When to use it

- Choosing the storage mode of a new or reworked model → [references/decision-guide.md](references/decision-guide.md).
- Building a model on Delta tables in a lakehouse, warehouse or other Fabric item; preparing those tables → [references/delta-table-checklist.md](references/delta-table-checklist.md).
- Controlling framing (refresh) during ETL, diagnosing fallback, guardrail errors or slow first queries.
- Migrating an Import model to Direct Lake → [references/migration-checklist.md](references/migration-checklist.md).
- Not for: star schema design → `powerbi-data-modeling`; DAX → `powerbi-dax-library`; M and Import refresh → `powerbi-power-query`; TMDL editing → `powerbi-tmdl`; deployment → `powerbi-alm`; role design and testing → `powerbi-governance`; capacity monitoring → `powerbi-operations`; query tuning → `powerbi-performance`. Creating Fabric items (lakehouse, notebooks, pipelines) belongs to the Microsoft Fabric skills when installed; otherwise give the user the steps and the documentation link.

## Choosing the storage mode

**Default: Import.** Choose **Direct Lake on OneLake** when the data is already curated Delta in OneLake (gold layer), the team owns or can change those tables, and the capacity guardrails fit the largest table. Use **Direct Lake on SQL analytics endpoint** only when you depend on SQL endpoint security or views; **DirectQuery** only for strict real time or sources that cannot land in OneLake. Full table, criteria and worked scenarios: [references/decision-guide.md](references/decision-guide.md).

## How it works, in plain words

- **Transcoding**: column data is loaded from the Delta/Parquet files into memory **on demand**, the first time a query needs that column. Loaded columns stay resident until evicted (reframing after a change, no use for some time, memory pressure).
- **Cold / warm**: the first query on cold columns pays the loading cost; later queries run at Import-like speed. A model can also return to cold after eviction or a move to another node. Warm up critical columns after reframing if first-query latency matters (run the main report queries).
- **Framing**: the model points to a given **version** of each Delta table. A "refresh" of a Direct Lake model is a reframe: a metadata operation, usually seconds, no data copy. Queries see the data as of the last successful framing, not necessarily the latest commit.
- **Automatic updates** (model setting, on by default at the time of writing): the model reframes whenever the Delta tables change. Turn it **off** and reframe explicitly at the end of the ETL when tables load at different times, so that facts and dimensions stay consistent. Details: [references/delta-table-checklist.md](references/delta-table-checklist.md#framing-and-etl-coordination).
- Mechanics: [How Direct Lake works](https://learn.microsoft.com/fabric/fundamentals/direct-lake-how-it-works).

## Design rules

1. **The star schema is built upstream** (gold layer) — Direct Lake tables have no Power Query step. Transformations, surrogate keys, the "Unknown" member and denormalized dimensions are produced by the ETL; the design itself follows `powerbi-data-modeling`.
2. **Typed columns, integer surrogate keys**, matching data types on both sides of each relationship, unique values on the one side (queries fail on duplicates). No high-cardinality text keys; split date and time.
3. **Unsupported column types** (complex Delta types, binary, GUID at the time of writing) are converted upstream.
4. **`Dim_Date` is a physical Delta table** in the lakehouse, marked as the date table. Do not rely on auto date/time.
5. **Delta table hygiene**: V-Order, compaction, few files and large row groups, VACUUM retention that keeps the framed version. Checklist: [references/delta-table-checklist.md](references/delta-table-checklist.md).
6. **No non-materialized SQL views** as Direct Lake on OneLake tables: materialize them as Delta tables (or a lakehouse materialized view), or bring that table in Import.
7. **Calculated columns and calculated tables**: avoid them. Direct Lake on OneLake supports them only in preview with limits (calculated columns in *User Context* only, not materialized, not usable in relationships); Direct Lake on SQL does not support them. Calculation groups and field parameters work in both.
8. **Measures do not change**: DAX written for Import works unchanged (`[Net Sales]`, `[Net Sales PY]`…), see `powerbi-dax-library`.
9. **Load only useful columns**: fewer columns means fewer to transcode and less memory.

## Guardrails

Limits per **capacity SKU** apply to each Direct Lake table: Parquet files per table, row groups per table, rows per table, plus model size on disk and memory available for paging. They change; **check the [Fabric capacity requirements](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview#fabric-capacity-requirements) table before sizing** and record the SKU and the largest table's counts in the design.

| Exceeded on | Direct Lake on OneLake | Direct Lake on SQL |
|---|---|---|
| Files, row groups or rows of a table | Framing fails and queries return errors until the tables are optimized or the SKU raised | Falls back to DirectQuery (if allowed): results still return, slower |
| Memory | Paging in and out, slower queries | Same |

## Security

Where RLS/OLS lives decides the behaviour. Summary (role design and testing stay in `powerbi-governance`):

| Rules defined in | Direct Lake on OneLake | Direct Lake on SQL |
|---|---|---|
| Semantic model roles (`RLS_Region`) | Supported; use a **fixed identity** cloud connection so users cannot bypass the model by reading the lake | Supported; same recommendation |
| OneLake security | Applied (OneLake roles, then model roles) | Not applicable |
| SQL analytics endpoint RLS / DDM / views | Not applied | Query **falls back** to DirectQuery |
| SQL analytics endpoint OLS / CLS | Not applied | Query **errors** on restricted objects |

- **SSO** (default): each user's own permissions on the source are checked; the user needs read access to the Fabric item. **Fixed identity**: one identity reads the data; users need no access to the lakehouse.
- Model roles are **not enforced** for users with Write permission on the model (workspace Admin, Member, Contributor). Test with a Viewer.
- The model **owner** must be able to read the source tables, otherwise framing fails.
- Reference: [Integrate Direct Lake security](https://learn.microsoft.com/fabric/fundamentals/direct-lake-security-integration).

## Fallback (Direct Lake on SQL only)

- Fallback reasons: SQL views, SQL endpoint RLS/DDM, guardrails exceeded, table not framed. Direct Lake on OneLake never falls back; it fails instead.
- `DirectLakeBehavior` model property: `Automatic` (default, silent fallback), `DirectLakeOnly` (fails loudly), `DirectQueryOnly`.
- **Default**: `DirectLakeOnly` in development and test, so that any fallback shows as an error. In production, Microsoft suggests `Automatic` so reports keep working; it also hides fallback, so pair it with a periodic `TABLETRAITS()` check (`powerbi-operations`). If you need fallback by design, prefer moving that table to Direct Lake on OneLake + Import.
- Detect: Performance analyzer shows a *Direct query* line for the visual; `EVALUATE TABLETRAITS()` returns a `[DirectLakeFallbackInfo]` column per table (`None` = Direct Lake); SQL Server Profiler shows `DirectQuery_Begin` / `DirectQuery_End` events. See [Analyze query processing](https://learn.microsoft.com/fabric/fundamentals/direct-lake-analyze-query-processing).

## Development workflow

1. Create the model from Power BI Desktop (OneLake catalog) or from the Fabric item; Desktop creates Direct Lake on OneLake models. Editing is **live**: every change applies to the model in the workspace, there is no local data and no publish step. Work in a development workspace.
2. For source control, export to a Power BI Project (PBIP) and keep editing against a remote model, one private remote model per developer (PBIP with Direct Lake is in preview at the time of writing). TMDL rules: `powerbi-tmdl`.
3. In TMDL, Direct Lake tables have partitions in `directLake` mode that point to a shared expression: `AzureStorage.DataLake` (OneLake) or `Sql.Database` (SQL endpoint). The workspace and item IDs in that expression differ per environment: parameterize them as text M parameters and set them at deployment (`powerbi-alm`). Never commit real IDs in examples.
4. After deployment, refresh (frame) the model, check the lineage points to the intended lakehouse, then run the non-regression queries of `powerbi-testing`.

## Process

1. Read the existing model, the source tables (row count, files, row groups, V-Order) and the capacity SKU.
2. Propose the storage mode with the decision table and the flavour of Direct Lake; list the gaps (calculated columns, Power Query logic, views, security location).
3. **Wait for approval** before converting a model or changing refresh, security or `DirectLakeBehavior` settings.
4. Execute, then verify: no fallback, guardrails respected, test parity, cold and warm timings recorded.
