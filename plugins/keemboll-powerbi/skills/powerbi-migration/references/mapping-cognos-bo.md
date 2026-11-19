# IBM Cognos Analytics and SAP BusinessObjects → Power BI

Both platforms put the business logic in a **governed semantic layer** (Cognos Framework Manager, BusinessObjects universe) and in **report-level formulas**. Migrate in that order: the layer first (it becomes the shared semantic model), then the reports. A report-by-report conversion copies the same rule into many places.

Every DAX "equivalent" below is a **pattern to test, not a guaranteed equivalent** (`powerbi-testing`). Column names other than those of the shared model are illustrative.

## IBM Cognos Analytics

### Concept mapping

| Cognos | Power BI | Notes |
|---|---|---|
| Framework Manager package | Shared semantic model | Rebuild as a star schema rather than copying the package layout (`powerbi-data-modeling`). |
| Data source query subject, model query subject | Source table or view; Power Query query | Heavy SQL inside a query subject belongs upstream (`powerbi-power-query`). |
| Query subject that acts as fact or as dimension depending on the query | Explicit fact and dimension tables | Cognos decides per query from the relationships. Power BI fixes the role in the model: decide it with the owner. |
| Determinants (group-by, unique) | Grain decisions: separate dimension tables, keys, relationship cardinality | Determinants tell the query engine how to avoid double counting on repeated data. In Power BI, repeated data must be split into the right table instead. |
| Relationships between query subjects | Relationships (single direction by default) | Check cardinality: an imported relationship is not proof of a correct one. |
| Data module (tables, table views, table copies, table unions) | Semantic model tables, appended or referenced queries | Same concepts under other names. |
| Model calculations, filters and prompts defined in the package | Measures, `RLS_<scope>` roles, slicers or `Param_*` tables | Record each in `MIGRATION.md` section 3 with its business intent. |
| Transformer PowerCubes, dimensionally modelled relational (DMR) models | Star-schema semantic model | Hierarchies become dimension attributes; rollups become measures. No conversion tool: rebuild. |
| Report Studio report (list, crosstab, chart) | Report page: table, matrix, chart | Rebuild for interaction (`powerbi-report-design`). |
| Report with pixel-level layout, bursting, long listings | Paginated report | See `mapping-excel-ssrs.md`. |
| Prompt pages (value, date, cascading prompts) | Slicers, or a filter page; cascading prompts become related slicers | Cascading across unrelated columns needs a relationship or a bridge. |
| Master-detail relationship | Drillthrough page or tooltip page | |
| Burst reports, schedules, saved output | Subscriptions, paginated report subscriptions | Check licensing and capacity (`powerbi-operations`). |
| Event Studio agents | Data alerts, Power Automate | List each agent and its action in `MIGRATION.md`. |
| Query Studio, Analysis Studio, Workspace | Report pages | Removed from Cognos Analytics 12.0.0 per IBM: existing Query Studio and Analysis Studio content still renders there. Check the IBM documentation for the release in use. |
| Content store, folders, roles | Workspaces, apps, workspace roles | `powerbi-governance`. |

### Report expressions

Cognos has two filter types that Power BI merges into one filter context:

| Cognos | Power BI | Notes |
|---|---|---|
| Detail filter (applied to rows before aggregation) | Filter on the column, or a filter inside `CALCULATE` | |
| Summary filter (applied after aggregation, at a grouping level) | Measure-based filter on the visual, or a measure returning blank | The scope of a summary filter depends on the grouping levels of the Cognos report: record them. |
| Detail aggregation / summary aggregation properties of a data item | The measure definition, plus the visual's own subtotal behaviour | A different aggregate at subtotal level (for example average in rows, total in the footer) needs `HASONEVALUE` / `ISINSCOPE` logic. |
| Summary functions with `for` / `at` clauses (`total ( [Revenue] for [Region] )`) | `CALCULATE` with `ALLEXCEPT` / `REMOVEFILTERS` / `ALLSELECTED` | The auto-generated `for` clause is implicit in Cognos: write down which grouping it used before translating. |

```dax
Net Sales Region Total =
// WHAT: net sales of the whole store region, ignoring the store on the row (Cognos total ( ... for [Region] ) pattern).
// NOTE: pattern to test, not a guaranteed equivalent. Region column illustrative.
CALCULATE ( [Net Sales], ALLEXCEPT ( Dim_Store, Dim_Store[Region] ) )
```

### Security

Cognos data security (model-layer filters, package and object permissions) → `RLS_<scope>` roles (rows) and OLS (objects), plus workspace and app permissions (`powerbi-governance`). Write each rule as a rule, not as a user list. Test "sees exactly" and "sees nothing" (`powerbi-testing`).

### Inventory

- Per report: package or data module used, prompts, filters, schedules and bursts, output formats, and the report expressions that carry business rules.
- Usage comes from the Cognos audit logging and the content store; check the IBM documentation for the release in use instead of assuming a menu path or table name. Ask for usage over 12 months: many reports run only at period end.
- Packages are **dependencies**: list which reports share a package and migrate the package first.
- IBM lifecycle dates move (11.1.x already left standard support in 2024 per IBM): add the platform move to `MIGRATION.md` section 7 after checking the IBM lifecycle page.

## SAP BusinessObjects

### Concept mapping

| BusinessObjects | Power BI | Notes |
|---|---|---|
| Universe (`.unx`, information design tool; `.unv`, universe design tool) | Shared semantic model | The universe is the migration unit. Classes become display folders, dimension objects become columns, measure objects become measures. |
| Joins, aliases, contexts | Relationships in a star schema | Contexts exist to resolve loops, chasm traps and fan traps: that is a **modelling alert**, not something to copy. Rebuild the grain explicitly. |
| Derived tables | Power Query or upstream views | |
| Object definitions using `@Select`, `@Where` | Measures or columns defined once | Resolve each `@` function to plain logic before translating. |
| `@Prompt` | Slicer or `Param_*` table | Value lists become slicers over the dimension. |
| `@Aggregate_Aware` | Aggregations, aggregate tables, or a single detailed table | Decide with the owner whether the aggregate table is still needed (`powerbi-performance`). |
| Web Intelligence document | Report | One report can hold several queries: see below. |
| Crystal Reports | Paginated report | See `mapping-excel-ssrs.md`. |
| Desktop Intelligence | Not available in 4.x | Convert to Web Intelligence first, then migrate, or rebuild. Check the SAP documentation. |
| Scheduled documents, publications | Subscriptions, paginated report subscriptions | |
| Lists of values | Slicer over a dimension | |

### Web Intelligence formulas

Context operators set which dimensions a calculation uses. They have no one-line equivalent: write the intent first.

| Web Intelligence | Meaning | Power BI pattern |
|---|---|---|
| `In ( [Year] )` | Calculate at exactly these dimensions | `CALCULATE ( [Net Sales], ALLEXCEPT ( Dim_Date, Dim_Date[Year] ) )` |
| `ForEach ( [Product] )` | Add a dimension to the calculation context | An iterator over `VALUES` of the added column, for example `SUMX ( VALUES ( Dim_Product[ProductKey] ), [Net Sales] )` |
| `ForAll ( [Quarter] )` | Remove a dimension from the context | `CALCULATE ( [Net Sales], REMOVEFILTERS ( Dim_Date[Quarter] ) )` |
| `Where ( [Year] = 2025 )` | Limit the data used by the measure | `CALCULATE ( [Net Sales], Dim_Date[Year] = 2025 )` |

Differences to test:

- In Web Intelligence the **block** of the report sets the default context. In Power BI the **visual** does. A formula that was correct in one block can change when the same measure lands in another visual.
- A dimension used in a `Where` clause can drop out of the calculation context (SAP notes this behaviour): compare results with and without it.
- **Merged dimensions** link several queries in one document. They have no equivalent: the shared dimension of the star schema replaces them. Check that each query's measure respects the merge by comparing totals (SAP documents a `ForceMerge` function because calculations ignore merged dimensions that are absent from the context).
- Variables in the document become measures or columns, depending on whether they aggregate.
- `ALLEXCEPT ( Dim_Date, ... )` clears the filters of the named table only: dimensions of other tables stay in the context. Decide with the owner which of them the `In` clause meant to keep.

### Security and administration

- Data security profiles (row and object restrictions, including restrictions that use the logged-in user) and security tables in the database → `RLS_<scope>` roles (rows) and OLS (objects). Restrictions that apply to every query in the universe must be reproduced for **every** report that uses the model.
- Usage and ownership: the BusinessObjects auditing database and the repository (query builder) give usage per document and per universe. Check the SAP documentation for the release in use.
- **Platform move**: SAP states that BI 4.3 reaches end of mainstream maintenance on 31 December 2026 (SAP knowledge base note 3763590) and that BI 2025 is available. Add the entry to `MIGRATION.md` section 7 after checking the current SAP maintenance strategy page; do not assert later dates from memory.

## Parity traps

| ID | Trap | Check |
|---|---|---|
| CB-01 | Counts and sums that were silently protected by determinants or universe contexts | Compare at the finest grain, then at each aggregation level |
| CB-02 | Subtotals that use a different aggregate than the detail rows | Compare the footer rows, not only the detail |
| CB-03 | Prompts defaulting to "all" or to a saved value | Run the same prompt values on both sides, including the default |
| CB-04 | Row restrictions applied in the semantic layer but not mentioned in the report | Compare as a restricted user, not as an administrator |
| CB-05 | Web Intelligence documents with several queries merged on a dimension | Compare each query's totals separately, then the merged block |
| CB-06 | Report-level calculated items (running totals, rank, percent of total) | Rebuild with `powerbi-dax-library` window patterns and test per sort order |
