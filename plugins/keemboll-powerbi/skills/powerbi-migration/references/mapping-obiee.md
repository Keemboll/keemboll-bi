# Oracle OBIEE / Oracle Analytics Server (RPD) → Power BI

Oracle's governed semantic layer is the **repository (RPD)**, now also called the semantic model in Oracle Analytics. Content built on it (analyses, dashboards, BI Publisher reports) queries **logical SQL** against the presentation layer. The migration unit is the RPD: it becomes the shared semantic model. Reports follow.

This reference covers OBIEE 11g and 12c, Oracle Analytics Server (OAS) and the semantic model of Oracle Analytics Cloud. Moving between Oracle products (OBIEE to OAS or Oracle Analytics Cloud) is an Oracle migration, outside this skill: Oracle documents it.

Every DAX "equivalent" below is a **pattern to test, not a guaranteed equivalent** (`powerbi-testing`). Column names other than those of the shared model are illustrative.

## Concept mapping

| Oracle | Power BI | Notes |
|---|---|---|
| Physical layer (tables, joins, connection pools, aliases) | Power Query sources, gateway or cloud connections | Re-create credentials in the target; never copy connection strings (rule 6 in `SKILL.md`). |
| Opaque view, `SELECT` physical table | Source view, Power Query query | Heavy SQL belongs upstream (`powerbi-power-query`). |
| Business model and mapping (BMM) layer | Semantic model | The layer that carries the business rules: inventory it first. |
| Logical fact table, logical dimension table | Fact and dimension tables | Check the star shape: logical joins are not proof of one. |
| Logical joins | Relationships | Logical SQL needs no join in the query, because the join comes from the model. Power BI relationships do the same, with a single direction by default. |
| Logical table source (LTS) | One physical table or view per Power BI table | A logical table with several sources (federation, fragmentation) means several tables to reconcile first. |
| Several LTS with priorities and content levels (aggregate navigation) | A single detailed table with aggregations, aggregate tables, or Direct Lake | Decide with the owner whether the aggregate sources are still needed (`powerbi-performance`, `powerbi-direct-lake`). |
| Logical dimension, level-based hierarchy (grand total level, levels, level keys) | Hierarchy in the dimension table | The grand total level becomes the "all" row in a matrix, not a table. |
| Parent-child hierarchy | Path columns built upstream or in Power Query | Rebuild with `PATH` functions or a flattened table. Test ragged branches. |
| Level-based measure (measure calculated at a dimension level) | `CALCULATE` with `ALLEXCEPT` / `REMOVEFILTERS` | See below. |
| Time dimension with a chronological key | `Dim_Date` with a sort-by column | `powerbi-data-modeling`. |
| Logical column with an aggregation rule (sum, count, average, last, first) | Measure | One measure per approved KPI (`powerbi-project`). |
| Calculated logical column | Power Query column, calculated column or measure | Choose by whether the value is row-level or aggregated. |
| Presentation layer (subject areas, folders, presentation hierarchies) | Display folders, hidden columns, perspectives | The subject area is a **view of the model**. Several subject areas on one model become several report entry points, not several models. |
| Repository variables (static, dynamic) | `Param_*` table, Power Query parameter, or a measure | A dynamic variable refreshed by an initialization block is a data-driven value: move it to a table. |
| Session variables, initialization blocks | RLS using `USERPRINCIPALNAME()` | See [Security](#security). |
| Analyses (Answers), dashboards, dashboard prompts | Report pages, slicers | Rebuild for interaction (`powerbi-report-design`). Presentation variables become slicers or `Param_*` tables. |
| BI Publisher reports, data models, templates | Paginated reports | See `mapping-excel-ssrs.md`. |
| Agents (alerts, scheduled delivery) | Data alerts, subscriptions | List each agent and its recipients by function in `MIGRATION.md`. |
| Catalog (folders, permissions, shared and personal content) | Workspaces and apps | Personal content is a hidden inventory: decide with the owner whether to include it. |

## Logical SQL and time series

Reports written in logical SQL or analyses with advanced expressions use functions that the Oracle BI Server resolves from the model. They have no one-line equivalent:

| Oracle | Power BI pattern to test | Notes |
|---|---|---|
| `AGO`, `TODATE`, `PERIODROLLING` (time series functions on a time dimension) | Time intelligence on `Dim_Date` | `powerbi-dax-library`. They rely on the chronological key of the time dimension: check that the calendar has the same keys, fiscal rules and boundaries. |
| `EVALUATE` (calls a database function) | Upstream computation (view or Power Query) | Native database calls have no DAX counterpart: rebuild the intent. |
| `FILTER ( measure USING condition )` | `CALCULATE ( measure, filter )` | Compare with the same dimension on the report. |
| Level-based measure, e.g. a total at the year level repeated on month rows | `CALCULATE ( [Net Sales], ALLEXCEPT ( Dim_Date, Dim_Date[Year] ) )` | Pattern to test. `ALLEXCEPT` clears only the filters of the named table. |
| Rank, running aggregates, moving average | Window functions or visual calculations | `powerbi-dax-library` is authoritative. Rewrite the sort and partition explicitly. |

```dax
Net Sales Year Total =
// WHAT: year total repeated on every month row (Oracle level-based measure at the Year level).
// NOTE: pattern to test, not a guaranteed equivalent. Year column illustrative.
CALCULATE ( [Net Sales], ALLEXCEPT ( Dim_Date, Dim_Date[Year] ) )
```

Fragmented sources have a documented limit in Oracle time series support (AGO, TODATE and PERIODROLLING are not supported on fragmented dimensional sources): a report that worked around it with several analyses needs its own parity test.

## Security

- Row-level security in an RPD is usually driven by **session variables** filled by **initialization blocks** (for example a query on a user-to-region table, or group membership) and applied as data filters on logical tables. Rebuild each as a security table plus an `RLS_<scope>` role that reads `USERPRINCIPALNAME()` (`powerbi-governance`).
- Identities differ: the user name in the Oracle repository is not necessarily the UPN Power BI returns. Map them before testing.
- Object permissions (presentation tables and columns hidden per group) → OLS, and workspace or app permissions for content. Keep them apart in `MIGRATION.md` section 4.
- Test "sees exactly" and "sees nothing" (`powerbi-testing`).

## Inventory

- Export the RPD as documentation (the Oracle repository documentation utility, check the Oracle documentation for the release) and list: logical tables and their sources, level-based measures, variables and initialization blocks, data filters, aggregate sources.
- Usage: Oracle usage tracking (logged queries per user and subject area) and the catalog. Check the Oracle documentation for the exact tables and settings in your release; turn it on before the inventory if it is off, then wait a full reporting cycle.
- List per analysis or dashboard: subject area, prompts, advanced logical SQL, and BI Publisher reports built on it.
- Many analyses are copies with different filters: group them before counting (step 2 of `SKILL.md`).
- **Platform move**: OBIEE 12c is at or past the end of its Oracle support window, and Oracle recommends moving to Oracle Analytics Server (Oracle announcements). Published dates differ by source: read the Oracle Support lifecycle note before writing a date in `MIGRATION.md` section 7.

## Parity traps

| ID | Trap | Check |
|---|---|---|
| OB-01 | Measures that aggregate differently by level (sum at day, average at month) | Compare at each hierarchy level and at the grand total |
| OB-02 | Aggregate navigation returning slightly different numbers from detailed and aggregate sources | Identify which source the Oracle query used, then compare to the same source |
| OB-03 | Time series functions on a fiscal calendar | Compare at fiscal year boundaries and at the first period of a year |
| OB-04 | Session variables set per user (default region, default period) | Compare as several distinct users, including a user with no value |
| OB-05 | Dashboard prompts with default values and presentation variables | Run the same prompt values on both sides |
| OB-06 | Outer-join behaviour in the logical model (dimension rows with no fact rows) | Compare row counts, not only totals |
