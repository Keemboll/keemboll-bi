# Base measures

```dax
Net Sales =
SUM ( Fact_Sales[NetAmount] )
```

```dax
Quantity =
SUM ( Fact_Sales[Quantity] )
```

```dax
Cost =
SUMX ( Fact_Sales, Fact_Sales[Quantity] * Fact_Sales[UnitCost] )
```

```dax
Order Count =
DISTINCTCOUNT ( Fact_Sales[OrderNumber] )
```

```dax
Customer Count =
DISTINCTCOUNT ( Fact_Sales[CustomerKey] )
```

With an SCD type 2, count the business key: `DISTINCTCOUNT ( Dim_Customer[CustomerCode] )` in a context filtered by the facts:

```dax
Customer Count (SCD2) =
CALCULATE (
    DISTINCTCOUNT ( Dim_Customer[CustomerCode] ),
    Fact_Sales
)
```

```dax
Average Basket =
DIVIDE ( [Net Sales], [Order Count] )
```

```dax
Weighted Average Price =
DIVIDE ( [Net Sales], [Quantity] )
```

```dax
Row Count =
COUNTROWS ( Fact_Sales )
```

Target from the budget fact (`TargetAmount` is an example column name; monthly grain, see the "Different grains" pattern of `powerbi-data-modeling`):

```dax
Sales Target =
SUM ( Fact_Budget[TargetAmount] )
```

Stock value (semi-additive: last date of the period, not a sum):

```dax
Closing Stock =
VAR _lastDate =
    LASTNONBLANK ( Dim_Date[Date], CALCULATE ( COUNTROWS ( Fact_Inventory ) ) )
RETURN
    CALCULATE ( SUM ( Fact_Inventory[Quantity] ), _lastDate )
```
