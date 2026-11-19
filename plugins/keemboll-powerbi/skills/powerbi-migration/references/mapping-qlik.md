# Qlik (QlikView, Qlik Sense) → Power BI

## The biggest conceptual change

Qlik's **associative model** links every table by field name and propagates any selection everywhere, including "excluded" values shown in grey. Power BI uses an **explicit star schema**: filters flow from dimensions to facts along single-direction relationships (`powerbi-data-modeling`). Consequences:

- A selection on one fact does **not** filter another fact unless both share a dimension.
- Synthetic keys and circular references in Qlik usually reveal a model problem: resolve them into a fact / dimension design, do not reproduce them with bidirectional relationships.
- "Possible / excluded" values (green / white / grey) have no direct equivalent. If users rely on seeing excluded values, discuss the need with the owner and design for it (e.g. a measure that flags rows without data).

Explain this to users before the parallel run: it is the first cause of "the numbers are different".

## Concept mapping

| Qlik | Power BI | Notes |
|---|---|---|
| Load script (`LOAD`, `SQL SELECT`, `JOIN`, `ApplyMap`, `Concatenate`) | Power Query or upstream ETL | `powerbi-power-query`; heavy transformations belong upstream. `ApplyMap` → merge or relationship. |
| QVD layers (extract / transform / model) | Lakehouse or warehouse tables, dataflows | The layering idea survives; the files do not. |
| Associative model, synthetic keys | Star schema, single-direction relationships | See above. |
| Master items (dimensions, measures) | Dimension columns, measures in `_Measures` | One measure per approved KPI (`powerbi-project`). |
| Set analysis `{< >}` | Filters inside `CALCULATE` | Patterns below. |
| `Aggr()` | Iterators (`SUMX`, `AVERAGEX`, `COUNTROWS ( FILTER ( ... ) )`) over `VALUES` or `SUMMARIZE` | Patterns below. |
| Variables (`$(vName)`) | Measures, or a `Param_*` table for user choices | A variable holding an expression becomes a measure. |
| Alternate states | No direct equivalent | Rebuild with disconnected tables and measures, or separate pages; test. |
| Section access | RLS (rows) and OLS (objects) | `powerbi-governance`. Section access reduces data at load; RLS filters at query time — test both "sees exactly" and "sees nothing" cases. |
| Bookmarks, sheets | Bookmarks, pages | |
| NPrinting / reports | Paginated reports or subscriptions | See `mapping-excel-ssrs.md`. |
| Charts and objects | Visuals | See [Visualisations](#visualisations). |
| Load script constructs | Power Query steps | See [Load script constructs](#load-script-constructs). |

## Set analysis — patterns to test, not guaranteed equivalents

Column names other than those of the shared model (`Dim_Date[Year]`, `Dim_Product[Category]`) are illustrative.

`Sum({<Year={2025}>} Sales)` — force a year, keep other selections:

```dax
Net Sales 2025 =
// NOTE: pattern to test, not a guaranteed equivalent. A fixed year belongs in KPI.md, not hard-coded long term.
CALCULATE ( [Net Sales], Dim_Date[Year] = 2025 )
```

`Sum({<Category=>} Sales)` — ignore the selection on one field:

```dax
Net Sales All Categories =
// NOTE: pattern to test, not a guaranteed equivalent.
CALCULATE ( [Net Sales], REMOVEFILTERS ( Dim_Product[Category] ) )
```

`Sum({1} Sales)` — ignore all selections:

```dax
Net Sales Grand Total =
// NOTE: pattern to test, not a guaranteed equivalent. RLS still applies in Power BI.
CALCULATE ( [Net Sales], REMOVEFILTERS () )
```

Set modifiers that **add** to a selection (`{<Year+={2024}>}`) or use element functions (`P()`, `E()`) have no one-line equivalent: write the intent, build the filter table explicitly (`UNION`, `EXCEPT`, `TREATAS`) and test.

## `Aggr()` — pattern to test

`Count({<>} Aggr(If(Sum(Sales) > 1000, Customer), Customer))` — customers above a threshold:

```dax
Customers Above Threshold =
// NOTE: pattern to test, not a guaranteed equivalent. The threshold is a business rule: put it in KPI.md or a Param_* table.
COUNTROWS (
    FILTER ( VALUES ( Dim_Customer[CustomerCode] ), [Net Sales] > 1000 )
)
```

## Set analysis — operators, `Total`, `Alt()`

Same rule: patterns to test. Column names are illustrative.

| Qlik | Meaning | Power BI pattern |
|---|---|---|
| `{<Year+={2024}>}` | add 2024 to the current selection | `CALCULATE ( [Net Sales], UNION ( VALUES ( Dim_Date[Year] ), TREATAS ( { 2024 }, Dim_Date[Year] ) ) )` |
| `{<Year-={2024}>}` | remove 2024 from the current selection | `CALCULATE ( [Net Sales], KEEPFILTERS ( Dim_Date[Year] <> 2024 ) )` |
| `{<Year*={2024}>}` | intersect the selection with 2024 | `CALCULATE ( [Net Sales], KEEPFILTERS ( Dim_Date[Year] = 2024 ) )` |
| `{<Year/={2024}>}` | symmetric difference | No one-liner: build the table with `UNION` / `EXCEPT` and test |
| `Sum(TOTAL Sales)` | ignore the chart dimensions, keep the selections | `CALCULATE ( [Net Sales], ALLSELECTED ( Dim_Product ) )` for the dimension used in the visual; use `REMOVEFILTERS ( Dim_Product )` to ignore the slicers too |
| `Sum(TOTAL <Year> Sales)` | ignore the dimensions except `Year` | `CALCULATE ( [Net Sales], ALLEXCEPT ( Fact_Sales, Dim_Date[Year] ) )` — as in `mapping-tableau.md`, this also clears filters on other dimensions of the fact |
| `Alt(a, b)` | first valid numeric value | `COALESCE ( a, b )` returns the first non-blank value, so a zero is kept and text is not skipped: test both cases |
| `P()` / `E()` (possible / excluded values) | values left or removed by other selections | No equivalent: write the intent, build the filter table, test |

Notes:

- `Year+=` only works when the selection is on `Year` itself: `VALUES` also respects filters on other `Dim_Date` columns (a `Date` range keeps cutting the added year). With `Year` on the visual axis, "add 2024" means "this row's year plus 2024". The literal must match the column's data type.
- `ALLEXCEPT ( Fact_Sales, ... )` clears filters of dimensions related to the fact, slicers included, which is stricter than `TOTAL <Year>`; dimensions not related to the fact are not cleared.
- `TOTAL` ignores the **chart dimensions**, while `REMOVEFILTERS` removes **filters on the named table or column**. A visual's dimension and a slicer both count as filters in DAX: decide with the owner which of them the Qlik expression meant to ignore.
- Selection-dependent expressions (`{$<...>}` versus `{1<...>}`, bookmark identifiers, `$(=expression)` dollar-sign expansion) change what "current selection" means. Record the identifier used in `MIGRATION.md` section 3 before choosing the pattern: `{1<...>}` ignores selections, `{$<...>}` keeps them.

## Load script constructs

The load script is migrated **layer by layer** (`powerbi-power-query` decides what stays in M and what goes upstream).

| Qlik script | Power BI | Notes |
|---|---|---|
| `Mapping LOAD` + `ApplyMap` | Merge with a lookup query, or a relationship | Prefer the relationship when the mapped column is a dimension attribute. |
| `Resident LOAD` | Referenced query | Keep the staging query not loaded into the model. |
| `Concatenate` | Append queries | Check that column names align first. |
| `Crosstable`, generic load | Unpivot / pivot | |
| `Qualify` / `Unqualify`, auto-linking by field name | Explicit column names and relationships | Field-name linking is the origin of most synthetic keys. |
| `Autonumber`, key composition | Surrogate keys created upstream | Do not rebuild keys in DAX. |
| `IntervalMatch` | Range join in the source, or a bridge table | Test boundaries (inclusive / exclusive). |
| `Peek()`, `Previous()`, `While` / `IterNo()` | Upstream ETL, or an index column plus a merge | Row-order logic is fragile in M: move it upstream when possible. |
| `For each` over files | Folder data source | Subfolders are included: filter the file list before combining. |
| Incremental load with QVD | Incremental refresh | `powerbi-power-query` (`RangeStart` / `RangeEnd`). The source must be filterable by date; an append-only QVD pattern does not translate to a plain file source. |
| Master calendar generated in script | `Dim_Date` | `powerbi-data-modeling`. |
| `Store ... into` QVD | Lakehouse or warehouse table | The intermediate QVD layer becomes a governed table. |

## Visualisations

Rebuild for Power BI's interaction model, not pixel for pixel (`powerbi-report-design`, `powerbi-mockup`).

| Qlik Sense object | Power BI | Notes |
|---|---|---|
| Bar, line, pie, scatter, treemap, gauge | Same-named visuals | Check sorting and "others" grouping. |
| Combo chart | Combo chart (line and clustered column) | |
| Straight table | Table | |
| Pivot table | Matrix | Subtotal and expand / collapse behaviours differ: test. |
| KPI object | Card or KPI visual | Conditional colours come from measures. |
| Filter pane | Slicers | Power BI slicers filter through model relationships by default; `TREATAS` or sync slicer groups are the exceptions (see the first section). |
| Container, tabbed objects | Bookmarks with buttons, or field parameters | No direct equivalent. |
| Text and image | Text box, image | |
| Map | Azure Maps, filled map, shape map, ArcGIS | The Bing-based map is announced for deprecation and Azure Maps must be enabled by an admin: check the Microsoft map overview for current status, regions and settings. |
| Extensions, mashups, Insight Advisor | No direct equivalent | List them in `MIGRATION.md` and decide with the owner. Closest for Insight Advisor: Copilot and smart narrative (check availability); the Q&A visual is announced for deprecation. |
| Master visualisations | Report theme and copied pages | No shared visual library as such. |

## Inventory

Before the keep / merge / retire decision, collect usage and ownership (`inventory-template.md`):

- **Qlik Sense on Windows**: the pre-installed Operations Monitor and License Monitor apps (content depends on version) and the management console are the usual sources of app usage, reload status and user access. **Qlik Cloud**: the administration activity center lists system and audit events; per-app usage usually needs the Audits API or the Qlik monitoring apps. UI labels and availability move: check the current Qlik documentation instead of assuming a menu path.
- **QlikView**: Server session and performance logs, configured in the management console, and the reload logs of the documents. Logging is often off or short-lived: check the QlikView help for your version.
- List per app: data connections, reload schedule, section access rule (as a rule, not a user list), variables, alternate states, extensions, NPrinting reports and bookmarks shared with users.
- Many Qlik apps are copies of one template with different selections: group them before counting (`powerbi-migration` step 2).
- Apps that load QVDs produced by other apps are **dependencies**: record the chain in `MIGRATION.md` section 1 (Sources) and migrate the producer first.
