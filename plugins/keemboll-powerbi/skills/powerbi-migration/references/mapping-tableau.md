# Tableau → Power BI

The goal is the **same answer to the same business question**, not the same formula. For each calculation: write its intent in business words (`MIGRATION.md`, section 3), pick the Power BI concept, then prove equality with a test (`powerbi-testing`).

## Concept mapping

| Tableau | Power BI | Notes |
|---|---|---|
| Data source / extract | Semantic model, Import mode | One shared model per subject area rather than one per workbook (`powerbi-data-modeling`). |
| Live connection | DirectQuery (or Direct Lake on Fabric, see `powerbi-direct-lake`) | Check performance early (`powerbi-performance`). |
| Blending, multiple data sources joined at view time | Relationships in a star schema | Blending is resolved per view; in Power BI the relationship is part of the model. Grain must be decided explicitly. |
| Calculated field, row-level (`[Price] * [Qty]`) | Power Query column (preferred) or calculated column | Push upstream when possible (`powerbi-power-query`). |
| Calculated field, aggregate (`SUM([Sales]) / SUM([Qty])`) | Measure | `powerbi-dax-library`. |
| LOD `FIXED` | `CALCULATE` with `ALLEXCEPT` / `REMOVEFILTERS` | See below — filter-order semantics differ. |
| LOD `INCLUDE` | Iterator over `VALUES` of the finer column | See below. |
| LOD `EXCLUDE` | `CALCULATE` with `REMOVEFILTERS` on the excluded column | See below. |
| Table calculations (running total, rank, % of total, moving average) | Window functions or visual calculations | `powerbi-dax-library` is authoritative. "Compute using" / partitioning must be rewritten explicitly. |
| Parameters | Field parameters, numeric range parameters, or a disconnected `Param_*` table | Parameters driving a calculation become a disconnected table read with `SELECTEDVALUE`. |
| Sets, groups | Grouping column in the dimension (Power Query or calculated column) | Dynamic sets (top N by condition) → measure-driven filter or TOPN pattern. |
| Dashboard actions (filter, highlight, URL, go to sheet) | Cross-filtering, drillthrough, bookmarks, buttons | Rebuild for Power BI's interaction model; mock up first (`powerbi-mockup`). |
| Context filters | Page / report filters, or filters inside `CALCULATE` | Affect LOD results: see below. |
| User filters, `USERNAME()` | RLS roles with `USERPRINCIPALNAME()` | `powerbi-governance`; test per `powerbi-testing`. |
| Tooltips, viz in tooltip | Report page tooltips | |
| Story points | Bookmarks and page navigation | No direct equivalent of the story format. |
| Tableau Prep flows | Power Query, dataflows or upstream ETL | |

## LOD expressions — patterns to test, not guaranteed equivalents

Why they differ: in Tableau, `FIXED` ignores dimension filters but **respects context filters** and data-source filters; `INCLUDE` / `EXCLUDE` respect dimension filters. In Power BI, every filter in the filter context reaches `CALCULATE` unless explicitly removed, and visual, page and report filters are not ordered like Tableau's filter pipeline. Each LOD therefore needs its own parity test, with and without the filters users apply.

**`{FIXED [Customer] : SUM([Sales])}`** — total of the customer, whatever else is in the view:

```dax
Net Sales per Customer =
// WHAT: net sales of the current customer, ignoring other filters (Tableau FIXED pattern).
// NOTE: pattern to test, not a guaranteed equivalent. Filters that were context filters in Tableau
//       must be re-applied explicitly or kept on columns outside the expanded Fact_Sales table.
CALCULATE (
    [Net Sales],
    ALLEXCEPT ( Fact_Sales, Dim_Customer[CustomerCode] )
)
```

`ALLEXCEPT` on the fact table removes filters from the fact table and every dimension related to it, except the listed column. If the Tableau sheet had a date **context** filter, keep that filter: add the exact column the filter uses (for example `Dim_Date[Year]`) to the `ALLEXCEPT` list — a filter on another date column would still be removed.

**`{INCLUDE [Customer] : SUM([Sales])}`** averaged in the view — average customer total:

```dax
Avg Net Sales per Customer =
// WHAT: average of customer totals in the current filter context (Tableau INCLUDE pattern).
// NOTE: pattern to test, not a guaranteed equivalent.
AVERAGEX ( VALUES ( Dim_Customer[CustomerCode] ), [Net Sales] )
```

**`{EXCLUDE [Product] : SUM([Sales])}`** — total ignoring the product in the view:

```dax
Net Sales All Products =
// WHAT: net sales ignoring any product filter (Tableau EXCLUDE pattern).
// NOTE: pattern to test, not a guaranteed equivalent.
CALCULATE ( [Net Sales], REMOVEFILTERS ( Dim_Product ) )
```

## No direct equivalent

- Tableau's filter order (extract → data source → context → dimension → measure → table calculation filters) as a whole: rebuild the intended behaviour and test it.
- Data blending's per-view aggregation of the secondary source.
- Pixel-exact layout of dashboards with floating objects: rebuild with `powerbi-report-design`.
