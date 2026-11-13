# Calendar-based time intelligence

**Preview feature.** When the Microsoft documentation was last read for this file, calendar-based time intelligence was a preview ("Enhanced DAX Time Intelligence", to enable in the Desktop preview features) that Microsoft recommends for flexibility and performance. Confirm its status, limits and UI labels on the current page before relying on it: <https://learn.microsoft.com/power-bi/transform-model/desktop-time-intelligence>. **The examples below were not executed.**

## Principle

A **calendar** is metadata defined on a table: it maps columns to time categories (Year, Quarter, Month, Week, Date, "of year" / "of quarter" variants, plus free "time-related" columns). A table can carry several calendars (Gregorian, fiscal, retail 4-4-5, 13 periods...). Time intelligence functions then take the **calendar name** instead of a date column, and week functions such as `TOTALWTD` become available.

Calendars are defined in Desktop (table → *Calendar options*), in the TMDL view or with external tools. Time-related columns can only be tagged through TMDL or external tools.

## Classic or calendar-based

| Situation | Choice |
|---|---|
| Gregorian calendar, or fiscal year that only shifts the start month | Classic ([time-intelligence.md](time-intelligence.md)) |
| Retail 4-4-5 / 4-5-4, 13 periods, lunar, any calendar that is not shifted Gregorian | Calendar-based |
| Week-based calculations (week to date, previous week) | Calendar-based (classic has no week function) |
| Date table with gaps that cannot be filled (closed days removed) | Calendar-based (no contiguous date column required) |
| Preview features not allowed in production, or model type listed as unsupported by the documentation | Classic |

## Rules

- Keep a dedicated `Dim_Date`, complete and marked as the date table (see `powerbi-data-modeling`): Microsoft still recommends it, and classic measures keep working.
- **One calendar per fiscal logic** (`'Fiscal Calendar'`, `'Retail Calendar'`), with a name that is unique in the model.
- Tag **only** the columns used in time calculations. A column cannot have two different categories across calendars.
- Each "partial" category (Month of Year, Week of Year...) needs its complement (Year...) so that a period is uniquely identified.
- Run the calendar validation (*Validate data*) and fix the warnings before writing measures.
- **Do not mix both styles for the same KPI**: `[Net Sales YTD]` is either classic or calendar-based, and its PY / change variants follow the same style.
- The "no future" bound of the classic patterns still applies.

## Calendar definition (TMDL)

Assumes `Dim_Date` has the columns `FiscalYear` and `FiscalYearMonth` (e.g. `FY2025-03`) in addition to `Date`. Check the exact syntax and the category keywords against the documentation.

```tmdl
ref table Dim_Date
	calendar 'Fiscal Calendar'
		calendarColumnGroup = year
			primaryColumn: FiscalYear

		calendarColumnGroup = month
			primaryColumn: FiscalYearMonth

		calendarColumnGroup = date
			primaryColumn: Date
```

`'Retail Calendar'` used below is built the same way with retail year and week columns; it must tag a Week category (or Week of Year + Year), otherwise week functions return an error.

## Example measures

```dax
Net Sales Fiscal YTD =
IF (
    MIN ( Dim_Date[Date] ) <= [_Last Sales Date],
    TOTALYTD ( [Net Sales], 'Fiscal Calendar' )
)
```

This replaces the classic `Net Sales Fiscal YTD` of [time-intelligence.md](time-intelligence.md): keep only one of the two in a model.

```dax
Net Sales WTD =
TOTALWTD ( [Net Sales], 'Retail Calendar' )
```

```dax
Net Sales Previous Week =
CALCULATE ( [Net Sales], DATEADD ( 'Retail Calendar', -1, WEEK ) )
```

```dax
Net Sales Fiscal PY =
CALCULATE ( [Net Sales], SAMEPERIODLASTYEAR ( 'Fiscal Calendar' ) )
```

## Pitfalls

- **Lateral or hierarchical shift.** `DATEADD` and `SAMEPERIODLASTYEAR` only shift laterally and keep the context on the other columns of the table. All other functions can shift hierarchically and **clear the filters** on the columns tagged in the calendar, including time-related ones: a slicer on a tagged `IsWorkday` column is ignored by `TOTALYTD` but kept by `DATEADD`. Filters on untagged columns are always kept.
- Several calendars on the same table: context clearing applies to all of them.
- A function fails if the calendar lacks the category it needs (`TOTALWTD` without a week category).
- Calendar-based functions cannot be nested: combine them with `CALCULATETABLE` instead.
- At date grain, results can differ from classic (a leap day shifted by a year); `DATEADD` has extension and truncation parameters for periods of unequal length.
- Limits listed by the documentation at the time of reading (to be confirmed): no live connected or composite models, no authoring in the service, not together with auto date/time, unexpected results when the calendar sits on a fact table subject to RLS.

## How to test

Apply `powerbi-testing`. Compare each calendar-based measure with a known result at **three grains** (year, month or period, week or day), on a period boundary (first and last week of the fiscal year) and with a slicer on a tagged column and on an untagged column.
