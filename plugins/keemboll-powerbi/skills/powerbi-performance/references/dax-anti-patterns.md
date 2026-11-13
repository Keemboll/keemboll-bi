# DAX — anti-patterns and rewrites

## 1. FILTER over a whole table

Before:

```dax
Web Sales =
CALCULATE ( [Net Sales], FILTER ( Fact_Sales, Fact_Sales[Channel] = "Web" ) )
```

After:

```dax
Web Sales =
CALCULATE ( [Net Sales], Fact_Sales[Channel] = "Web" )
```

If the filter must **keep** the existing filter on the column (intersection rather than replacement):

```dax
Web Sales =
CALCULATE ( [Net Sales], KEEPFILTERS ( Fact_Sales[Channel] = "Web" ) )
```

## 2. Filter on a measure: iterate the dimension, not the fact

Before:

```dax
Large Customer Sales =
CALCULATE ( [Net Sales], FILTER ( Fact_Sales, [Net Sales] > 10000 ) )
```

After (the threshold applies per customer, on the dimension column):

```dax
Large Customer Sales =
CALCULATE (
    [Net Sales],
    FILTER ( VALUES ( Dim_Customer[CustomerCode] ), [Net Sales] > 10000 )
)
```

If the dimension is **SCD2**, filter on the business key `CustomerCode` (one row per customer), not on the surrogate key `CustomerKey` (one row per version). **To be tested.**

## 3. Repeated expressions

Before:

```dax
Net Sales Change % =
IF ( [Net Sales PY] = 0, BLANK (), ( [Net Sales] - [Net Sales PY] ) / [Net Sales PY] )
```

After:

```dax
Net Sales Change % =
VAR _py = [Net Sales PY]
RETURN
    DIVIDE ( [Net Sales] - _py, _py )
```

## 4. Existence

Before:

```dax
Has Purchased = IF ( COUNTROWS ( FILTER ( Fact_Sales, Fact_Sales[Quantity] > 0 ) ) > 0, 1 )
```

After:

```dax
Has Purchased =
IF ( NOT ISEMPTY ( CALCULATETABLE ( Fact_Sales, Fact_Sales[Quantity] > 0 ) ), 1 )
```

## 5. Densification with zeros

Before:

```dax
Net Sales Displayed = IF ( ISBLANK ( [Net Sales] ), 0, [Net Sales] )
```

Effect: every product × customer combination shows a row → huge queries.

After: keep `[Net Sales]` as is. If displaying 0 is required, limit the 0 to the items **already present** in the context (e.g. months of the selected period) rather than the whole Cartesian product:

```dax
Net Sales Displayed =
VAR _sales = [Net Sales]
RETURN
    IF ( ISBLANK ( _sales ) && ISINSCOPE ( Dim_Date[YearMonth] ), 0, _sales )
```

Or use the visual option *Show items with no data* on the relevant axis only.

## 6. Iterator at the wrong grain

Before (iterates every sales row):

```dax
Avg Net Sales per Customer =
AVERAGEX ( Fact_Sales, [Net Sales] )
```

After (iterates customers):

```dax
Avg Net Sales per Customer =
AVERAGEX ( VALUES ( Dim_Customer[CustomerCode] ), [Net Sales] )
```

If the dimension is **SCD2**, iterate over `CustomerCode` (business key): with `CustomerKey`, a customer with several versions would count several times. **To be tested.**

## 7. SWITCH to select a measure

`SWITCH` stops at the first matching value: the following branches are not evaluated (the order of conditions matters). So it is not a performance problem. To select a measure from a slicer, a **field parameter** or a **calculation group** is still preferable for **usability** (no formula to maintain for every new indicator), not for speed.
