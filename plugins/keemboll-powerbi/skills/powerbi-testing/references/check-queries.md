# DAX check queries

> **Not executed here**: no DAX engine was available at writing time. Each query must be validated on a real model (DAX Studio or the DAX query view of Power BI Desktop) before being considered reliable.

Example model: `Fact_Sales` (`CustomerKey`, `OrderDate`, `NetAmount`), `Dim_Customer` (`CustomerKey` surrogate key, `CustomerCode` business key), `Dim_Product` (`Category`), `Dim_Date` (`Date`, `Year`, `YearMonth`), `Dim_Store` (`Region`), measure `[Net Sales]`. Adjust the names; keep the WHAT / EXPECTED header.

Unless stated otherwise, **expected = zero rows**.

## Level 1 — model integrity

### Duplicate key in a dimension

```dax
// WHAT: no duplicate key in Dim_Customer.
// EXPECTED: zero rows.
EVALUATE
FILTER (
    SUMMARIZECOLUMNS ( Dim_Customer[CustomerKey], "Row Count", COUNTROWS ( Dim_Customer ) ),
    [Row Count] > 1
)
```

If the relationship already exists, the engine guarantees uniqueness on the "one" side: this test is mostly useful before creating the relationship, or on the business key (`CustomerCode`, which may legitimately repeat with SCD2 — see `powerbi-data-modeling`).

### Blank keys in facts

```dax
// WHAT: no sales row without a customer or a date.
// EXPECTED: 0 and 0.
EVALUATE
ROW (
    "No Customer", COUNTROWS ( FILTER ( Fact_Sales, ISBLANK ( Fact_Sales[CustomerKey] ) ) ) + 0,
    "No Date", COUNTROWS ( FILTER ( Fact_Sales, ISBLANK ( Fact_Sales[OrderDate] ) ) ) + 0
)
```

### Referential integrity fact → dimension

```dax
// WHAT: every customer key in sales exists in Dim_Customer.
// EXPECTED: zero rows (otherwise: list of orphan keys).
EVALUATE
EXCEPT (
    DISTINCT ( Fact_Sales[CustomerKey] ),
    DISTINCT ( Dim_Customer[CustomerKey] )
)
```

Variant that weighs the gap (rows attached to the blank row of the dimension):

```dax
// WHAT: weight of sales without a known customer.
// EXPECTED: 0 orphan rows.
EVALUATE
ROW (
    "Orphan Rows",
        COUNTROWS ( FILTER ( Fact_Sales, ISBLANK ( RELATED ( Dim_Customer[CustomerKey] ) ) ) ) + 0
)
```

If the dimension carries an "Unknown" row (key -1, see `powerbi-data-modeling`), orphans are attached to it upstream and these tests do not see them: also count `COUNTROWS ( FILTER ( Fact_Sales, Fact_Sales[CustomerKey] = -1 ) ) + 0` and track that number.

### Continuous date table covering the facts

```dax
// WHAT: Dim_Date has no gap and covers all order dates.
// EXPECTED: [Day Count] = [Expected Day Count]; [First Day] <= [Min Facts]; [Last Day] >= [Max Facts].
EVALUATE
VAR _min = MIN ( Dim_Date[Date] )
VAR _max = MAX ( Dim_Date[Date] )
RETURN
    ROW (
        "First Day", _min,
        "Last Day", _max,
        "Day Count", COUNTROWS ( Dim_Date ),
        "Expected Day Count", DATEDIFF ( _min, _max, DAY ) + 1,
        "Min Facts", MIN ( Fact_Sales[OrderDate] ),
        "Max Facts", MAX ( Fact_Sales[OrderDate] )
    )
```

Repeat for each related date column (`DeliveryDate`...).

## Level 2 — reconciliation with the source

```dax
// WHAT: monthly control totals to compare with the source system extract.
// EXPECTED: each row equals the source total of the same month, within the agreed tolerance.
EVALUATE
SUMMARIZECOLUMNS (
    Dim_Date[YearMonth],
    "Row Count", COUNTROWS ( Fact_Sales ),
    "Net Amount", SUM ( Fact_Sales[NetAmount] )
)
ORDER BY Dim_Date[YearMonth]
```

Compare **row count** and **amount**: the former reveals join duplicates and forgotten filters, the latter sign or currency errors. Do the comparison outside the repository; record only *pass / fail*.

## Level 3 — measures

### Total = sum of details (additive measures only)

```dax
// WHAT: total [Net Sales] equals the sum by category.
// EXPECTED: [Gap] = 0.
EVALUATE
VAR _total = [Net Sales]
VAR _sum = SUMX ( VALUES ( Dim_Product[Category] ), [Net Sales] )
RETURN
    ROW ( "Total", _total, "Sum of Details", _sum, "Gap", _total - _sum )
```

With `VALUES`, the blank row of orphan facts is **included** in the sum: a non-zero gap points to a non-additive measure or a filter specific to the measure, not to orphans. To weigh the orphans, replace `VALUES` with `DISTINCT ( Dim_Product[Category] )`, which excludes that blank row: the resulting gap is then their amount.

### Known case

```dax
// WHAT: [Net Sales] of year 2025 for a given category.
// EXPECTED: value provided by the business (not written here).
EVALUATE
CALCULATETABLE (
    ROW ( "Net Sales", [Net Sales] ),
    Dim_Date[Year] = 2025,
    Dim_Product[Category] = "Accessories"
)
```

### Edge behavior

```dax
// WHAT: measures on a period without sales (year outside the history).
// EXPECTED: [Net Sales] blank, no error, no misleading 0, no infinity.
EVALUATE
CALCULATETABLE (
    ROW ( "Net Sales", [Net Sales], "Net Sales Is Blank", ISBLANK ( [Net Sales] ) ),
    Dim_Date[Year] = 1999
)
```

Reuse this pattern for: first year of the history (no prior year), zero denominator, selection of several years, incomplete current year.

## Level 4 — regression

Compare the old and the new formula in the same query, without touching the model:

```dax
// WHAT: the new writing of [Net Sales] gives the same values by month and category.
// EXPECTED: zero rows.
DEFINE
    MEASURE Fact_Sales[Net Sales New] = SUM ( Fact_Sales[NetAmount] )
EVALUATE
FILTER (
    SUMMARIZECOLUMNS (
        Dim_Date[YearMonth],
        Dim_Product[Category],
        "Before", [Net Sales],
        "After", [Net Sales New]
    ),
    ABS ( [Before] - [After] ) > 0.005
        || ISBLANK ( [Before] ) <> ISBLANK ( [After] )
)
```

- Choose axes that cover the filters actually used by the report (`powerbi-lean`, `usage` subcommand).
- For a model change (relationship, Power Query): run the same query before and after, export both results outside the repository, compare.

## Level 5 — RLS

Run **under the tested role** (DAX Studio connected to the model: advanced connection options, role / effective user; "View as" in Desktop for the report).

```dax
// WHAT: identity seen by the engine and visible scope for the RLS_Region role.
// EXPECTED: only the regions of the test profile; total = sum of those regions.
EVALUATE
ROW ( "User", USERPRINCIPALNAME () )

EVALUATE
SUMMARIZECOLUMNS ( Dim_Store[Region], "Net Sales", [Net Sales] )
ORDER BY Dim_Store[Region]
```

```dax
// WHAT: user missing from the security table.
// EXPECTED: 0 visible rows.
EVALUATE
ROW ( "Visible Rows", COUNTROWS ( Fact_Sales ) + 0 )
```

## Level 6 — report

No generic query: copy the visual's query from the Performance analyzer in Desktop, run it, and compare with the values tested at levels 2 and 3. Check by hand: slicers, interactions between visuals, bookmarks, drillthrough, tooltips, empty states. Performance: `powerbi-performance`.
