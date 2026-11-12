---
name: powerbi-dax-library
description: "Library of standard DAX measures: base measures, time intelligence (year to date, prior year, % change, rolling 12 months, moving average), margins, share of total, rankings, Top N, new customers, calculation groups, field parameters and switches through disconnected tables (Plan/PY, Top/Bottom, Monthly/Cumulative). Use to write, complete or fix DAX measures so that validated patterns are reused instead of reinventing formulas. Triggers: DAX, measure, YTD, cumulative, prior year, PY, YoY, growth, variance, share, ratio, rank, RANKX, Top N, moving average, time intelligence, calculation group, switch, disconnected table, SELECTEDVALUE, dynamic title."
---

# DAX library

Apply `powerbi-conventions` (naming, format, description) and `powerbi-performance` (efficient patterns). The patterns assume a star schema with `Dim_Date` marked as the date table (see `powerbi-data-modeling`).

## Method

1. **Search first** in the model for an existing measure that already does the calculation; reuse it.
2. Start from a **base measure** (`[Net Sales]`, `[Quantity]`, `[Customer Count]`) and compose.
3. Adapt the library pattern: replace the generic names (`Fact_Sales`, `Dim_Date`, `[Measure]`) with those of the real model.
4. Add description, format and display folder.
5. **Test** with a check query (see below) on a scope whose result is known.

## Catalog

| Family | Measures | Reference |
|---|---|---|
| Base | Sum, row count, distinct count, weighted average | [base](references/base-measures.md) |
| Time | YTD, QTD, MTD, PY, PY YTD, change, % change, rolling 12 months, moving average, last known value | [time-intelligence](references/time-intelligence.md) |
| Ratios | Margin, margin %, share of total, share of parent, contribution | [ratios](references/ratios-rankings.md#ratios) |
| Rankings | Rank, Top N + Others, ABC / Pareto | [rankings](references/ratios-rankings.md#rankings) |
| Customers | Active, new, lost customers | [customers](references/ratios-rankings.md#customers) |
| Dynamic | Time calculation group, field parameter, dynamic format | [time-intelligence](references/time-intelligence.md#calculation-group) |
| Switches | Plan / PY, Top / Bottom, Monthly / Cumulative through disconnected tables, dynamic titles and colors | [switches](references/switches.md) |

## Library rules

- Time intelligence: always through `Dim_Date[Date]`, never through a date of the fact table.
- Hide future values: time measures return `BLANK()` beyond the last data date (`_Last Sales Date` measure provided in `references/time-intelligence.md`).
- Percentages are ratios (0.15) formatted `0.0%`, not values × 100.
- No `FORMAT()` in a numeric measure.

## Check query

To run in the DAX query view of Desktop, DAX Studio or through MCP:

```dax
EVALUATE
SUMMARIZECOLUMNS (
    Dim_Date[Year],
    Dim_Date[MonthNum],
    "Net Sales", [Net Sales],
    "Net Sales PY", [Net Sales PY],
    "Change %", [Net Sales Change %]
)
ORDER BY Dim_Date[Year], Dim_Date[MonthNum]
```
