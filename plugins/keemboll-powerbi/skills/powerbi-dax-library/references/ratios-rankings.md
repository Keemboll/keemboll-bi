# Ratios, rankings, customers

## Ratios

```dax
Gross Margin =
[Net Sales] - [Cost]
```

```dax
Gross Margin % =
DIVIDE ( [Gross Margin], [Net Sales] )
```

Share of the grand total (ignores the filters of the product dimension):

```dax
Share of Sales % =
DIVIDE ( [Net Sales], CALCULATE ( [Net Sales], REMOVEFILTERS ( Dim_Product ) ) )
```

Share of the parent in a hierarchy (category → subcategory → product). **To be tested.**

```dax
Share of Category % =
DIVIDE (
    [Net Sales],
    CALCULATE (
        [Net Sales],
        REMOVEFILTERS ( Dim_Product[Subcategory], Dim_Product[Product] )
    )
)
```

The denominator removes the filters of **every level below the category**: the measure returns the share within the category whether the visual stops at the subcategory or goes down to the product (removing only `Subcategory` would give 100% at product level). Slicers set on the other columns of `Dim_Product` are kept. At category level the result is 100%. Add the other lower-level columns of the hierarchy if it has any.

Share that keeps the slicer filters (`ALLSELECTED`):

```dax
Share of Visible Sales % =
DIVIDE ( [Net Sales], CALCULATE ( [Net Sales], ALLSELECTED ( Dim_Product ) ) )
```

## Rankings

```dax
Product Rank =
IF (
    ISINSCOPE ( Dim_Product[Product] ),
    RANKX ( ALLSELECTED ( Dim_Product[Product] ), [Net Sales],, DESC, DENSE )
)
```

Top N + "Others": prefer the native **Top N** visual filter. If an "Others" row is required, create a disconnected table of labels, `Products_TopN[Product]` (the products + "Others"), and put it on the visual:

```dax
Net Sales Top N =
VAR _n = 10
VAR _product = SELECTEDVALUE ( Products_TopN[Product] )
VAR _top =
    TOPN ( _n, ALLSELECTED ( Dim_Product[Product] ), [Net Sales] )
RETURN
    IF (
        _product = "Others",
        CALCULATE ( [Net Sales], EXCEPT ( ALLSELECTED ( Dim_Product[Product] ), _top ) ),
        IF (
            _product IN SELECTCOLUMNS ( _top, "p", Dim_Product[Product] ),
            CALCULATE ( [Net Sales], Dim_Product[Product] = _product )
        )
    )
```

`_n = 10` is a default: drive it with a numeric parameter if users must choose N.

ABC class (Pareto 80 / 15 / 5):

```dax
ABC Class =
VAR _sales = [Net Sales]
VAR _total = CALCULATE ( [Net Sales], ALLSELECTED ( Dim_Product[Product] ) )
VAR _cumulative =
    SUMX (
        FILTER (
            ALLSELECTED ( Dim_Product[Product] ),
            [Net Sales] >= _sales
        ),
        [Net Sales]
    )
VAR _pct = DIVIDE ( _cumulative, _total )
RETURN
    IF (
        ISINSCOPE ( Dim_Product[Product] ) && NOT ISBLANK ( _sales ),
        SWITCH ( TRUE (), _pct <= 0.8, "A", _pct <= 0.95, "B", "C" )
    )
```

Expensive on large dimensions: compute the class upstream beyond roughly 10,000 products (default threshold).

## Customers

Active customers over the period = `[Customer Count]` (see [base-measures.md](base-measures.md)).

If `Dim_Customer` is an **SCD type 2**, count the business key `CustomerCode` (the surrogate key `CustomerKey` changes with each version of the customer); `SUMMARIZE` starts from the facts, so each set is evaluated in its own date context. Measures **to be tested**.

New customers (first purchase within the period):

```dax
New Customers =
VAR _start = MIN ( Dim_Date[Date] )
VAR _customersInPeriod = SUMMARIZE ( Fact_Sales, Dim_Customer[CustomerCode] )
VAR _customersBefore =
    CALCULATETABLE (
        SUMMARIZE ( Fact_Sales, Dim_Customer[CustomerCode] ),
        Dim_Date[Date] < _start,
        REMOVEFILTERS ( Dim_Date )
    )
RETURN
    COUNTROWS ( EXCEPT ( _customersInPeriod, _customersBefore ) )
```

Lost customers (active in the prior year, inactive in the period):

```dax
Lost Customers =
VAR _customersPY =
    CALCULATETABLE (
        SUMMARIZE ( Fact_Sales, Dim_Customer[CustomerCode] ),
        SAMEPERIODLASTYEAR ( Dim_Date[Date] )
    )
VAR _customersCY = SUMMARIZE ( Fact_Sales, Dim_Customer[CustomerCode] )
RETURN
    COUNTROWS ( EXCEPT ( _customersPY, _customersCY ) )
```

With a long history, materialize the first purchase date in `Dim_Customer` (upstream) and compare it with the period: much faster.
