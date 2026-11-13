# Date table

## Requirements

- One row per day, **no gaps**, complete years.
- `Date` column of date type, unique → **Mark as date table**.
- Sort columns (`MonthNum`, `WeekdayNum`) linked to the labels through *Sort by column*.
- Ideally provided by the source (Warehouse/Lakehouse); otherwise Power Query; DAX as a last resort.

## DAX version (calculated table)

```dax
Dim_Date =
VAR _start =
    DATE (
        YEAR ( MIN ( MIN ( Fact_Sales[OrderDate] ), MIN ( Fact_Sales[DeliveryDate] ) ) ),
        1,
        1
    )
VAR _end =
    DATE (
        YEAR ( MAX ( MAX ( Fact_Sales[OrderDate] ), MAX ( Fact_Sales[DeliveryDate] ) ) ),
        12,
        31
    )
RETURN
    ADDCOLUMNS (
        CALENDAR ( _start, _end ),
        "Year", YEAR ( [Date] ),
        "Quarter", "Q" & QUARTER ( [Date] ),
        "MonthNum", MONTH ( [Date] ),
        "Month", FORMAT ( [Date], "mmmm", "en-US" ),
        "YearMonth", FORMAT ( [Date], "yyyy-mm" ),
        "WeekdayNum", WEEKDAY ( [Date], 2 ),
        "Weekday", FORMAT ( [Date], "dddd", "en-US" ),
        "IsWorkday", WEEKDAY ( [Date], 2 ) <= 5
    )
```

The bounds cover **all** the fact date columns used in the model (here `OrderDate` and `DeliveryDate`): add or remove a column in the `MIN` / `MAX` according to the dates actually related to `Dim_Date`. With `OrderDate` alone, a delivery outside that range would have no row in `Dim_Date`. To be tested. The locale in `FORMAT` (`en-US`) is a default: use the language of the report.

## Power Query (M) version

```powerquery
let
    StartDate = #date(2020, 1, 1),
    EndDate = #date(Date.Year(DateTime.LocalNow()) + 1, 12, 31),
    Days = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, Days, #duration(1, 0, 0, 0)),
    Source = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(Source, {{"Date", type date}}),
    Year = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    MonthNum = Table.AddColumn(Year, "MonthNum", each Date.Month([Date]), Int64.Type),
    Month = Table.AddColumn(MonthNum, "Month", each Date.MonthName([Date], "en-US"), type text),
    Quarter = Table.AddColumn(Month, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    WeekdayNum = Table.AddColumn(Quarter, "WeekdayNum", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    Weekday = Table.AddColumn(WeekdayNum, "Weekday", each Date.DayOfWeekName([Date], "en-US"), type text)
in
    Weekday
```

The `2020` and `+1` bounds are defaults: set them to the real history. `powerbi-power-query` is authoritative for M code rules.

## Fiscal year

If the fiscal year does not start in January (e.g. October 1st), add `FiscalYear` and `FiscalMonthNum`, and pass the fiscal year-end date to the time intelligence functions: `DATESYTD ( Dim_Date[Date], "9/30" )` (month/day format; check according to the model's language).

For a calendar that is not a shifted Gregorian one (4-4-5, 13 periods, week-based), add the period columns to `Dim_Date` and see calendar-based time intelligence in `powerbi-dax-library`.
