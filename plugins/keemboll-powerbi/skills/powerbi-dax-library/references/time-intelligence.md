# Time intelligence

Assumption: `Dim_Date` marked as the date table, related to the main date of the facts. Replace `[Net Sales]` with the base measure needed.

These are the **classic** patterns (date column as argument). For fiscal calendars that are not shifted Gregorian (4-4-5, 13 periods) or week-based calculations, see [calendar-time-intelligence.md](calendar-time-intelligence.md).

## "No future" bound

Reused in the measures below to avoid displaying running totals over months without data.

```dax
_Last Sales Date =
CALCULATE ( MAX ( Fact_Sales[OrderDate] ), REMOVEFILTERS () )
```

## Running totals

```dax
Net Sales YTD =
IF (
    MIN ( Dim_Date[Date] ) <= [_Last Sales Date],
    CALCULATE ( [Net Sales], DATESYTD ( Dim_Date[Date] ) )
)
```

Fiscal year (e.g. ending September 30): same "no future" bound, fiscal year-end date as the second argument. **To be tested.**

```dax
Net Sales Fiscal YTD =
IF (
    MIN ( Dim_Date[Date] ) <= [_Last Sales Date],
    CALCULATE ( [Net Sales], DATESYTD ( Dim_Date[Date], "9/30" ) )
)
```

The format of the end date (`"9/30"`, month/day) depends on the model's language. See the "Fiscal year" section of `powerbi-data-modeling/references/dim-date.md`, or drive the date with a parameter measure.

```dax
Net Sales QTD =
CALCULATE ( [Net Sales], DATESQTD ( Dim_Date[Date] ) )
```

```dax
Net Sales MTD =
CALCULATE ( [Net Sales], DATESMTD ( Dim_Date[Date] ) )
```

## Prior-year comparison

```dax
Net Sales PY =
CALCULATE ( [Net Sales], SAMEPERIODLASTYEAR ( Dim_Date[Date] ) )
```

```dax
Net Sales YTD PY =
CALCULATE ( [Net Sales YTD], SAMEPERIODLASTYEAR ( Dim_Date[Date] ) )
```

```dax
Net Sales Change =
VAR _cy = [Net Sales]
VAR _py = [Net Sales PY]
RETURN
    IF ( NOT ISBLANK ( _cy ) && NOT ISBLANK ( _py ), _cy - _py )
```

```dax
Net Sales Change % =
VAR _cy = [Net Sales]
VAR _py = [Net Sales PY]
RETURN
    IF ( NOT ISBLANK ( _cy ), DIVIDE ( _cy - _py, _py ) )
```

## Rolling period

```dax
Net Sales Rolling 12 Months =
VAR _end = MAX ( Dim_Date[Date] )
RETURN
    IF (
        _end <= [_Last Sales Date],
        CALCULATE (
            [Net Sales],
            DATESINPERIOD ( Dim_Date[Date], _end, -12, MONTH )
        )
    )
```

**To be tested.**

```dax
Net Sales 3-Month Moving Average =
VAR _end = MAX ( Dim_Date[Date] )
RETURN
    IF (
        _end <= [_Last Sales Date],
        CALCULATE (
            AVERAGEX ( VALUES ( Dim_Date[YearMonth] ), [Net Sales] ),
            DATESINPERIOD ( Dim_Date[Date], _end, -3, MONTH )
        )
    )
```

- The filter on `Dim_Date[Date]` replaces the visual's filter: the measure works whatever the axis, provided `Dim_Date` is **marked as the date table** (otherwise the visual's filter on `YearMonth` stays active).
- `AVERAGEX` ignores the months whose `[Net Sales]` is `BLANK`: a month without sales is not counted as 0, the average covers the non-empty months of the window. To count those months as 0, use `[Net Sales] + 0` in the iterator.

## Cumulative since the beginning

```dax
Net Sales Cumulative =
VAR _end = MAX ( Dim_Date[Date] )
RETURN
    CALCULATE (
        [Net Sales],
        Dim_Date[Date] <= _end,
        REMOVEFILTERS ( Dim_Date )
    )
```

## Last known value

`[Price]` stands for any base measure of a fact that is not filled every day.

```dax
Last Known Price =
VAR _date =
    LASTNONBLANK ( Dim_Date[Date], [Price] )
RETURN
    CALCULATE ( [Price], _date )
```

## Calculation group

Avoids duplicating each measure into YTD / PY / Change %. Table `CG_Time`, column `Time Calculation`.

| Item | Expression | Format |
|---|---|---|
| Current | `SELECTEDMEASURE ()` | — |
| YTD | `CALCULATE ( SELECTEDMEASURE (), DATESYTD ( Dim_Date[Date] ) )` | — |
| PY | `CALCULATE ( SELECTEDMEASURE (), SAMEPERIODLASTYEAR ( Dim_Date[Date] ) )` | — |
| Change % | see below | `"0.0%"` |

```dax
VAR _cy = SELECTEDMEASURE ()
VAR _py = CALCULATE ( SELECTEDMEASURE (), SAMEPERIODLASTYEAR ( Dim_Date[Date] ) )
RETURN
    IF ( NOT ISBLANK ( _cy ), DIVIDE ( _cy - _py, _py ) )
```

Calculation groups apply to **all** measures: exclude measures that are already time-based, or ratios, if needed with `ISSELECTEDMEASURE`.

## Field parameter

Created through Modeling → New parameter → Fields. Lets the user choose the measure or dimension displayed. Name it `Param_Metric` / `Param_Axis`.
