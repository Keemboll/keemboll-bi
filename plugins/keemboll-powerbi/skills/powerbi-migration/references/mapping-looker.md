# Looker (LookML) → Power BI

There is no Microsoft migration tool. Looker is **code-first**: the model is LookML files in Git, and every query is generated as SQL against the database. Power BI is **model-first**: tables, relationships and measures are stored in the semantic model and evaluated by its engine. Map by concept and prove equality with tests (`powerbi-testing`).

Looker Studio is a different product with no LookML: confirm which one the source is before using this reference.

Every DAX "equivalent" below is a **pattern to test, not a guaranteed equivalent**. Column names other than those of the shared model are illustrative.

## Concept mapping

| Looker | Power BI | Notes |
|---|---|---|
| LookML project (Git repository) | PBIP project (Git) | Good news: both are versioned text. Keep the review habit (`powerbi-alm`). |
| Model file (connection, includes, explores) | Semantic model | One model per subject area, not one per explore (`powerbi-data-modeling`). |
| View | Table (Power Query query or source table) | A view over a table is a table; a view with `derived_table` is a query. |
| Explore | Entry point to part of the model | One LookML explore is a joined subset. In Power BI the whole model is available: decide which tables a report page uses. |
| Join (`sql_on`, `type`, `relationship`) | Relationship, cardinality and direction | The grain is fixed by the model, not by the explore: see [Fanout and symmetric aggregates](#fanout-and-symmetric-aggregates). |
| Dimension | Column (Power Query or calculated column) | Push row-level logic upstream (`powerbi-power-query`). |
| `dimension_group` (timeframes) | Columns of `Dim_Date` | Only if the shared calendar table has the same attributes. Time zones: see parity traps. |
| Measure (`sum`, `count`, `count_distinct`, `average`, `min`, `max`, `number`) | Measure | `number` measures that combine other measures map to a compound measure. |
| Filtered measure (`filters: [ ... ]`) | `CALCULATE` with the filter | Check whether the filter overrides or keeps the slicer on the same column (`KEEPFILTERS`). |
| Derived table, native (`explore_source`) or SQL-based | Power Query, upstream view, dataflow or lakehouse table | Heavy logic belongs upstream. |
| Persistent derived table (PDT) and its datagroup (`datagroup_trigger`, `sql_trigger_value`, `persist_for`) | Upstream table plus a refresh schedule or pipeline trigger | The trigger logic (rebuild when the ETL finishes) becomes the refresh dependency: `powerbi-operations`. |
| Parameters, templated filters, Liquid | `Param_*` tables read with `SELECTEDVALUE`, field parameters | Dynamic SQL has no equivalent: rebuild the intent. With several values selected, `SELECTEDVALUE` returns its default (or blank): decide the multi-select behaviour. |
| Table calculations | Visual calculations or measures | `powerbi-dax-library`; check the current Microsoft documentation for the status of visual calculations. |
| Merged results (several queries in one tile) | Several visuals, or a model with a shared dimension | Merged results join query outputs on dimension values: the shared dimension of the star schema replaces them. |
| Looks, dashboards, dashboard filters | Report pages, slicers (sync slicers for report-wide filters) | Rebuild for interaction (`powerbi-report-design`). |
| Schedules, alerts | Subscriptions, data alerts | |
| Folders, content access | Workspaces and apps | `powerbi-governance`. |

## Fanout and symmetric aggregates

When a join multiplies rows (one-to-many), a plain `SUM` on the "one" side overcounts. Looker computes **symmetric aggregates** to avoid it: they are on by default per explore, controlled by the `relationship` parameter of each join, and require a unique, non-null primary key on each view (Looker documents the error it raises when the key is not unique). The effect: a measure defined on **any** view returns the right number whatever the join.

Power BI does not do this for you:

- A measure is evaluated on its own table with the filters that reach it. Filters flow from the "one" side to the "many" side: a measure computed on a dimension table is **not** filtered by a column of the fact table unless the relationship filters both ways (a last resort, see `powerbi-data-modeling`) or the measure goes through the fact table.
- Measures defined in LookML on a dimension view (for example a customer count or a customer-level sum) must be rebuilt as `DISTINCTCOUNT` over the key, or as an iterator over `VALUES` of the key, when the visual also uses columns from a fact table.
- Many-to-many joins in LookML (`relationship: many_to_many`) are a modelling alert: introduce a bridge table instead of a many-to-many relationship (`powerbi-data-modeling`).

```dax
Customer Count =
// WHAT: distinct customers in the current filter context (Looker count_distinct on the primary key).
// NOTE: pattern to test, not a guaranteed equivalent. Compare with and without a Fact_Sales filter.
DISTINCTCOUNT ( Dim_Customer[CustomerKey] )
```

## Security

| Looker | Power BI | Notes |
|---|---|---|
| `access_filter` with a user attribute | RLS role (`RLS_<scope>`) | Rows. Test "sees exactly" and "sees nothing" (`powerbi-testing`). |
| `access_grant` with `required_access_grants` on an explore, join, view or field | OLS, plus workspace permissions | Objects. Looker's grant is an exact match on the user attribute value, and user-editable attributes are not allowed (Looker documentation). Power BI OLS works on tables and columns: check the Microsoft documentation for what it can hide. |
| `sql_always_where` (fixed for everyone), `always_filter` (visible, changeable) | A filter in the source query or view; a default slicer or filter | Not RLS. |
| User attributes | Security table, or `USERPRINCIPALNAME()` | Map the identity first: the Looker email is not necessarily the UPN. |

## Inventory

- Content usage comes from Looker's System Activity Explores (History, Content Usage; retention is limited). Check the Looker documentation for the current model names and ask for usage before the keep / merge / retire decision.
- List per Look or dashboard: explores, filters, schedules and access rules (as rules, not user lists).
- Count the views that are **derived tables** or PDTs: they hide ETL that Power BI will not run for you.
- List the datagroups: they show the refresh dependencies the upstream pipeline must reproduce.
- Dashboards built on LookML dashboards (code) and user-defined dashboards may live in different places: check both.

## Parity traps

| ID | Trap | Check |
|---|---|---|
| LK-01 | Measures that were protected by symmetric aggregates | Compare totals with a one-to-many join on the visual |
| LK-02 | Time zone conversion of date columns (`convert_tz`, query time zone, user time zone) | Compare around midnight and month boundaries |
| LK-03 | `dimension_group` timeframes (week start day, fiscal year) | Compare week and fiscal-year columns on boundary dates |
| LK-04 | Filtered measures that override or keep the dashboard filter | Compare with the filter applied and cleared |
| LK-05 | Table calculations computed on the pivoted result, in the tile's sort order | Rewrite the sort and partition explicitly, then compare |
| LK-06 | Default values of parameters and dashboard filters | Run the same selections on both sides |
