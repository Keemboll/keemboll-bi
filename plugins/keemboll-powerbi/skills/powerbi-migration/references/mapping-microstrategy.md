# MicroStrategy (Strategy) → Power BI

The vendor now brands the product **Strategy** (Strategy One). Documentation, object names and menus still carry both names: search under both. Since Strategy One (March 2024), dossiers are called dashboards. Check the current vendor documentation before naming a feature to the owner.

MicroStrategy separates a **schema layer** (attributes, facts, hierarchies, transformations) from an **application layer** (metrics, filters, prompts, reports, dashboards). The schema layer becomes the star schema; the application layer becomes measures, slicers and report pages. Every DAX "equivalent" below is a **pattern to test, not a guaranteed equivalent** (`powerbi-testing`). Column names other than those of the shared model are illustrative.

## Concept mapping

| MicroStrategy | Power BI | Notes |
|---|---|---|
| Project (schema and application objects) | Shared semantic model plus reports | One model per subject area, not per project (`powerbi-data-modeling`). |
| Attribute, attribute forms (ID, description) | Dimension column with a key and a description column | Keep the key for relationships and the description for display; sort the description by the key when the order matters. |
| Hierarchy (user or system) | Hierarchy in the dimension table | Drill paths are rebuilt as hierarchies and drillthrough pages. |
| Fact | Numeric column of a fact table | Facts that exist at several grains (several fact tables) need separate fact tables and shared dimensions. |
| Metric (simple, compound) | Measure | One measure per approved KPI (`powerbi-project`). |
| Level (dimensionality) metric | `CALCULATE` with `ALLEXCEPT` / `REMOVEFILTERS` | See [Level metrics](#level-metrics). |
| Conditional metric (metric with a filter) | `CALCULATE` with the filter inside | |
| Transformation (last year, month to date) | Time intelligence on `Dim_Date` | `powerbi-dax-library`. Test the calendar boundaries. |
| Filter (attribute, metric qualification, set) | Slicer, filter pane, or a filter inside `CALCULATE` | Metric qualifications (filter on a metric value) become measure-based filters or `TOPN` patterns. |
| Prompt (value, element list, hierarchy, object) | Slicer, field parameter, or `Param_*` table | Object prompts (choose the metric or attribute) become field parameters. |
| Consolidation (calculations across attribute elements shown as rows) | Calculation group, or a disconnected table with measures | No direct equivalent: write the intent per row. |
| Custom group (banding with filters) | Grouping column in the dimension, or a disconnected band table | |
| Derived elements | Grouping column or measure | |
| Report (grid or graph) | Matrix, table or chart | Rebuild for interaction (`powerbi-report-design`). |
| Dashboard / dossier | Report with pages, bookmarks and buttons | Rebuild; do not copy the layout (`powerbi-mockup`). |
| Report Services document, pixel layout | Paginated report | See `mapping-excel-ssrs.md`. |
| Intelligent Cube, in-memory dataset | Import model, or Direct Lake on Fabric | Cubes cannot contain consolidations or custom groups (vendor documentation): those objects become model logic. Storage mode: `powerbi-direct-lake`. |
| Library, subscriptions, distribution | Apps, subscriptions | `powerbi-operations`. |
| Database instances, warehouse catalog | Power Query sources, gateways | Re-create credentials in the target; never copy connection strings (rule 6 in `SKILL.md`). |

## Level metrics

By default a MicroStrategy metric is calculated at the **report level**: the attributes on the report dictate the aggregation. A level (dimensionality) changes that, with three parts: a **target** attribute, a **grouping** option and a **filtering** option. Document the three for every level metric before writing DAX.

| Level element | Meaning (vendor documentation) | Power BI pattern to test |
|---|---|---|
| Target | The attribute at which the metric is calculated | The column kept or removed in the filter context |
| Grouping standard | Aggregate by the target's level | The visual's own grouping, or `ALLEXCEPT` on the target |
| Grouping none | No grouping on the target or its children | `REMOVEFILTERS` on the target and its lower levels |
| Filtering ignore | Ignore report-filter conditions on the target and its parents and children | `REMOVEFILTERS` on the target's table or columns |
| Filtering absolute | Raise the report filter to the level of the target, then apply it | `ALLEXCEPT` on the target's table, keeping the filter on the target |
| Filtering none | Leave the relationship with the report filter unspecified | Default behaviour of `CALCULATE` without a filter modifier |

```dax
Net Sales All Products =
// WHAT: net sales of all products, ignoring the product on the row (MicroStrategy Revenue {Product} with ignore filtering pattern).
// NOTE: pattern to test, not a guaranteed equivalent. Product filters from slicers are removed too.
CALCULATE ( [Net Sales], REMOVEFILTERS ( Dim_Product ) )

Net Sales Share of Products =
// WHAT: contribution metric, net sales divided by net sales of all products.
// NOTE: pattern to test.
DIVIDE ( [Net Sales], [Net Sales All Products] )
```

Notes:

- A level written as `{~+, Year+}` means "report level plus year". The `~` is the report level: it has no fixed column, so the DAX version depends on the visual. Test with the same attributes on the grid.
- Metrics based on non-aggregatable facts (inventory, balances) use the grouping options "beginning" or "ending" lookup or fact. Map them to a last-value or semi-additive measure (`powerbi-dax-library`) and test at each time grain.
- Level metrics default to filtering on attributes that are not on the report unless the project setting says otherwise (a legacy option from old projects): note the project setting in `MIGRATION.md`.

## Security

- **Security filters** (row-based, assigned to users or groups, including those driven by a relational table) → `RLS_<scope>` roles. When the rules come from a database table, model that table as a security table and reproduce the join (`powerbi-governance`).
- Security roles and privileges (who can create, schedule, export) → workspace roles and tenant settings, which are not row filters. Keep the two apart in `MIGRATION.md` section 4.
- Test "sees exactly" and "sees nothing" for each filter (`powerbi-testing`).

## Inventory

- Platform Analytics (the vendor's telemetry tool, which replaced Enterprise Manager for most uses) gives content, cube, subscription and user activity. Check the vendor documentation for the release in use.
- List per dashboard or report: the metrics it uses (and which are level metrics, transformations or consolidations), prompts, the cubes it reads, subscriptions, and security filters that apply.
- Many dashboards read the same cubes: migrate the **cube** (the future semantic model) before the dashboards, and record the dependency in `MIGRATION.md` section 1 (Sources).
- Vendor partners offer metadata export and conversion accelerators. Treat their output as a draft: it goes through steps 3 to 5 of `SKILL.md` like any other mapping.

## Parity traps

| ID | Trap | Check |
|---|---|---|
| MS-01 | Metrics calculated at the report level that change when an attribute is added to the grid | Compare with the same attributes, then with one more |
| MS-02 | Level metrics with absolute versus ignore filtering | Test with a filter on a child attribute and one on the target |
| MS-03 | Transformations (last year, year to date) built on a different calendar than `Dim_Date` | Compare at year boundaries and for leap days |
| MS-04 | Consolidations and custom groups that overlap or leave rows out | Compare group totals against the grand total |
| MS-05 | Prompt defaults and saved prompt answers | Run the same answers on both sides |
| MS-06 | Security filters applied per user rather than per group | Compare as each distinct filter case |
