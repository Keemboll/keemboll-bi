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
| Formulas and functions | DAX or M | See [Functions](#functions). |
| Sheets and marks | Visuals | See [Visualisations](#visualisations). |

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

## Table calculations

Tableau's "compute using" (table down, across, specific dimensions) has no setting in Power BI: the partition and the order are **written explicitly**. Ask the author of each sheet what "compute using" was, then pick the tool (`powerbi-dax-library` is authoritative for the patterns).

| Tableau | Power BI | Notes |
|---|---|---|
| `RUNNING_SUM`, `RUNNING_AVG` | Visual calculation `RUNNINGSUM`, or `WINDOW` / `CALCULATE` over dates | Visual calculations depend on the visual's layout. A running average is a running sum divided by a running count: write it explicitly. |
| `WINDOW_SUM`, `WINDOW_AVG`, moving average | `WINDOW` with `ORDERBY` and `PARTITIONBY` in a measure, or visual calculation `MOVINGAVERAGE` | State the window size and whether the current row is included. `MOVINGAVERAGE` exists only as a visual calculation; there is no moving sum shortcut (use `SUMX` over `WINDOW`, or `RANGE`). |
| `RANK`, `RANK_DENSE`, `RANK_UNIQUE`, `RANK_MODIFIED`, `RANK_PERCENTILE` | `RANKX`, or `RANK` with `SKIP` / `DENSE`; `ROWNUMBER` with a tie-breaker in `ORDERBY` for `RANK_UNIQUE` | `RANK_MODIFIED` and `RANK_PERCENTILE`: no direct function, build and test. Tableau ranks descending by default and ignores nulls: state the order and the blank handling. `RANK` needs an explicit table, `ORDERBY` and `PARTITIONBY`. |
| `LOOKUP ( expr, n )` | `OFFSET`, or visual calculations `PREVIOUS` / `NEXT` | |
| `INDEX()` (row number) | `ROWNUMBER`, or `RANK` with dense ties over a window | DAX `INDEX ( n, ... )` returns the **row at position n**, a different thing. |
| `FIRST()`, `LAST()` (offsets from the current row, not values) | Rewrite from the use, e.g. "versus first": visual calculation `FIRST`, or `INDEX ( 1, ... )` | |
| `PREVIOUS_VALUE` (recursive) | No equivalent | Needs a different design (cumulative logic or upstream); test. |
| `TOTAL`, percent of total | `DIVIDE ( [Net Sales], CALCULATE ( [Net Sales], ALLSELECTED () ) )` pattern | Pattern to test: "percent of what" (grand total, column, parent) must be decided. It keeps slicer and page filters (`ALL` would give the share of the whole model) and shows 100% when one row is displayed. For a percent of parent, use `REMOVEFILTERS` on the child column. In a visual calculation, use `COLLAPSE` (parent) or `COLLAPSEALL` (grand total). |

Visual calculations live on one visual: no reuse, no pinning to dashboards, not exported, unsupported on some visual types. Prefer `WINDOW` / `OFFSET` in a measure when the logic must be shared, and check the Microsoft *Visual calculations overview* page for the current limits.

## Functions

| Tableau | DAX / M | Notes |
|---|---|---|
| `IF` / `ELSEIF` / `CASE` | `IF`, `SWITCH ( TRUE (), ... )` | |
| `ZN ( x )`, `IFNULL ( x, y )` | `COALESCE ( x, 0 )`, `COALESCE ( x, y )` | Tableau null and DAX blank are not identical: in DAX `BLANK () = 0` is true. Apply `COALESCE` at display level only: in a measure it turns blank into 0 and every member then shows a row. |
| `ISNULL` | `ISBLANK` | |
| `ATTR ( [Field] )` | `SELECTEDVALUE ( <column>, "*" )` | `ATTR` returns `*` for several values and ignores nulls (confirm on the Tableau aggregation page); `SELECTEDVALUE` returns blank for several values or none unless the second argument is given (it then replaces both cases). On a versioned dimension use the stable business key (`CustomerCode`). |
| `COUNTD` | `DISTINCTCOUNTNOBLANK` | `DISTINCTCOUNT` counts blank as a value; `COUNTD` ignores nulls. |
| `DATEDIFF ( 'month', a, b )` | `DATEDIFF ( a, b, MONTH )` | Argument order differs. Both count interval boundaries crossed, not whole elapsed units. Week start differs (Tableau has a start-of-week argument): test. |
| `DATETRUNC`, `DATEPART` | Columns of `Dim_Date`, or `DATE ( YEAR ( d ), MONTH ( d ), 1 )` | Prefer a calendar column (`powerbi-data-modeling`). `STARTOFMONTH` returns the first date visible in the filter context: it does not truncate a value. |
| `CONTAINS`, `FIND`, `STR`, `LEFT` | `CONTAINSSTRING`, `SEARCH` / `FIND`, `FORMAT`, `LEFT` | `FIND` argument order is reversed (DAX: text to find first, then the text searched). `FIND` is case-sensitive, `SEARCH` and `CONTAINSSTRING` are not (`CONTAINSSTRINGEXACT` is). |
| `TODAY ()`, `NOW ()` | `TODAY ()`, `NOW ()` | Evaluated at query time in a measure, at refresh in a column or table; check the time zone with the owner. |

Check the Microsoft DAX reference for each function before use.

## Visualisations

Rebuild for Power BI's interaction model, not pixel for pixel (`powerbi-report-design`, `powerbi-mockup`).

| Tableau | Power BI | Notes |
|---|---|---|
| Bar, line, area, pie, scatter, treemap | Same-named visuals | Check sorting and "others" grouping. |
| Dual axis | Line and clustered column chart, or a secondary axis | Synchronised axes need a decision. |
| Text table, crosstab | Table or matrix | |
| Highlight table, heat map | Matrix with conditional formatting | |
| Map (symbol, filled) | Azure Maps visual, or the older map / filled map / shape map visuals | Azure Maps is generally available except in sovereign clouds and the older visuals are planned for deprecation: check the current Microsoft map overview and the tenant setting for Azure Maps. |
| Reference lines, bands, trend lines | Analytics pane lines, or measures | Distribution bands are not identical: test. |
| Dashboard containers, device layouts | Page layout, mobile layout | Floating objects: see below. |
| Filter shown on a sheet | Slicer | Tableau "apply to worksheets" scopes become *Edit interactions* settings, visual by visual. |
| Extensions, custom shapes | No direct equivalent, or custom visuals | List them in `MIGRATION.md` and decide with the owner. |

## Inventory

Before the keep / merge / retire decision, collect usage and ownership (`inventory-template.md`):

- **Tableau Server or Tableau Cloud**: usage, extract refresh status and ownership come from the administrative views, the Tableau REST and Metadata APIs, and on Tableau Cloud the Admin Insights data source. On Tableau Server the Metadata API must be enabled by an administrator; on Tableau Cloud it may need a licence. Names and availability move: check the current Tableau documentation instead of assuming a menu path.
- **Files**: a `.twb` holds the definition and no data; a `.twbx` is a zip of the workbook plus any local data sources, extracts and images. Archive it untouched (rule 1 of `SKILL.md`).
- List per workbook: published versus embedded data sources, extracts versus live, refresh schedule, user filters and `USERNAME()` rules (as rules, not user lists), parameters, LOD and table calculations, actions, subscriptions and alerts.
- Published data sources shared by several workbooks are the natural **shared models**: group by data source before counting workbooks (`powerbi-migration` step 2).
- Calculated fields copied between workbooks with small differences are common: compare them before mapping, and send the differences to the owner.
