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
