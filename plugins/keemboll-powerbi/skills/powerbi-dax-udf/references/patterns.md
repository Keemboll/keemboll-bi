# Function patterns

Six functions on the shared model (`Fact_Sales`, `Dim_Date`, `Dim_Product`, `[Net Sales]`). Each block gives the function as it is written in a DAX query (`DEFINE`) and a measure that calls it. To store a function in the model, use the TMDL form of [tmdl-and-testing.md](tmdl-and-testing.md). Test each one with the query template of the same file before saving it.

The calling measures follow `powerbi-conventions` (description, format, display folder) and the formulas follow `powerbi-dax-library`.

## 1. Safe percentage change

```dax
DEFINE
    /// Relative change between two values; BLANK when either value is BLANK or the reference is zero.
    /// @param {SCALAR VARIANT VAL} current - Value of the period being analyzed
    /// @param {SCALAR VARIANT VAL} reference - Value it is compared to
    /// @returns Ratio (0.15 = +15%), to format 0.0% in the calling measure
    FUNCTION Ratio.PctChange = ( current : SCALAR VARIANT VAL, reference : SCALAR VARIANT VAL ) =>
        IF (
            NOT ISBLANK ( current ) && NOT ISBLANK ( reference ),
            DIVIDE ( current - reference, reference )
        )
```

```dax
Net Sales Change % =
// WHAT: Net sales of the period compared to the prior year, in %.
// HOW: Ratio.PctChange of [Net Sales] against [Net Sales PY].
Ratio.PctChange ( [Net Sales], [Net Sales PY] )
```

`VARIANT` keeps a BLANK argument BLANK instead of casting it (see rule 2 of the skill).

## 2. Year-over-year % for any measure

Calls pattern 1. `metric` is `EXPR` so that it is re-evaluated under the prior-year dates.

```dax
DEFINE
    /// Year-over-year change of any measure or scalar expression, through the date column passed.
    /// @param {SCALAR NUMERIC EXPR} metric - Measure or expression to compare, evaluated inside the function
    /// @param {COLUMNREF} dateColumn - Date column of the marked date table
    /// @returns Ratio of change versus the same period last year; BLANK when either year is BLANK
    FUNCTION Period.YoYPct = ( metric : SCALAR NUMERIC EXPR, dateColumn : COLUMNREF ) =>
        VAR _current = metric
        VAR _prior = CALCULATE ( metric, SAMEPERIODLASTYEAR ( dateColumn ) )
        RETURN
            Ratio.PctChange ( _current, _prior )
```

```dax
Gross Margin YoY % =
// WHAT: Gross margin compared to the same period last year, in %.
// HOW: Period.YoYPct over Dim_Date[Date].
Period.YoYPct ( [Gross Margin], Dim_Date[Date] )
```

Hiding future periods (`_Last Sales Date` in `powerbi-dax-library`) stays in the calling measure or in the measure passed as `metric`.

## 3. Share of total over a column

```dax
DEFINE
    /// Share of a value in its total once the filters on one column are removed.
    /// @param {SCALAR NUMERIC EXPR} metric - Measure or expression to divide
    /// @param {COLUMNREF} scopeColumn - Column whose filters are removed for the denominator
    /// @returns Ratio between 0 and 1 for additive measures; BLANK when the total is BLANK or zero
    FUNCTION Ratio.ShareOfTotal = ( metric : SCALAR NUMERIC EXPR, scopeColumn : COLUMNREF ) =>
        DIVIDE ( metric, CALCULATE ( metric, REMOVEFILTERS ( scopeColumn ) ) )
```

```dax
Net Sales Share of Product =
// WHAT: Share of the product in the net sales of all products, in %.
// HOW: Ratio.ShareOfTotal over Dim_Product[Product]; other filters (dates, stores) are kept.
Ratio.ShareOfTotal ( [Net Sales], Dim_Product[Product] )
```

`REMOVEFILTERS` ignores slicers on that column. For a share of the visible selection, write a second function with `ALLSELECTED ( scopeColumn )` rather than adding a mode flag.

## 4. ABC class from a cumulative share

The cumulative share itself comes from the ABC pattern of `powerbi-dax-library`; the function only turns it into a class. Thresholds are parameters (rule 3 of the skill).

```dax
DEFINE
    /// ABC class (Pareto) of an item from its cumulative share of the total.
    /// @param {SCALAR VARIANT VAL} cumulativeShare - Cumulative share, from 0 to 1, of the item ranked by value
    /// @param {SCALAR NUMERIC VAL} aLimit - Upper bound of class A (for example 0.8)
    /// @param {SCALAR NUMERIC VAL} bLimit - Upper bound of class B (for example 0.95)
    /// @returns "A", "B", "C", or BLANK when the share is BLANK
    FUNCTION Band.ABC = (
            cumulativeShare : SCALAR VARIANT VAL,
            aLimit : SCALAR NUMERIC VAL,
            bLimit : SCALAR NUMERIC VAL
        ) =>
        SWITCH (
            TRUE (),
            ISBLANK ( cumulativeShare ), BLANK (),
            cumulativeShare <= aLimit, "A",
            cumulativeShare <= bLimit, "B",
            "C"
        )
```

```dax
Product ABC Class =
// WHAT: ABC class of the product on net sales.
// HOW: Band.ABC of the hidden cumulative share; thresholds 80 / 95 come from KPI.md.
Band.ABC ( [_Net Sales Cumulative Share], 0.8, 0.95 )
```

## 5. Compact number for titles

Returns **text**: use it in titles, labels and tooltips only, never in a numeric measure (`powerbi-dax-library` rule on `FORMAT()`).

```dax
DEFINE
    /// Number written in short form for titles: 1.2 K, 3.4 M, 5.6 bn.
    /// @param {SCALAR VARIANT VAL} value - Number to write
    /// @param {SCALAR INT64 VAL} decimals - Decimals shown after the short unit
    /// @param {SCALAR STRING VAL} locale - Locale passed to FORMAT, for example "en-US"
    /// @returns Text, or BLANK when the value is BLANK
    FUNCTION Fmt.Compact = (
            value : SCALAR VARIANT VAL,
            decimals : SCALAR INT64 VAL = 1,
            locale : SCALAR STRING VAL = "en-US"
        ) =>
        VAR _abs = ABS ( value )
        VAR _pattern = IF ( decimals > 0, "0." & REPT ( "0", decimals ), "0" )
        RETURN
            SWITCH (
                TRUE (),
                ISBLANK ( value ), BLANK (),
                _abs >= 1000000000, FORMAT ( value / 1000000000, _pattern, locale ) & " bn",
                _abs >= 1000000, FORMAT ( value / 1000000, _pattern, locale ) & " M",
                _abs >= 1000, FORMAT ( value / 1000, _pattern, locale ) & " K",
                FORMAT ( value, "#,##0", locale )
            )
```

```dax
Title Net Sales =
// WHAT: Dynamic title of the sales page.
// HOW: Fmt.Compact of [Net Sales]; default decimals and locale.
"Net sales: " & Fmt.Compact ( [Net Sales] )
```

## 6. SVG progress bar

Builds the image for a table or matrix. Apply the SVG rules of `powerbi-html-visuals` (data category Image URL, `%23` for `#`, decimal point, `viewBox`). Colors are parameters: the caller takes them from the theme.

```dax
DEFINE
    /// Horizontal progress bar as an SVG data URI, 100 x 10 units.
    /// @param {SCALAR VARIANT VAL} ratio - Progress from 0 to 1; values outside are clipped
    /// @param {SCALAR STRING VAL} barColor - Bar color, URL-encoded (for example "%231F4E79")
    /// @param {SCALAR STRING VAL} trackColor - Background color, URL-encoded
    /// @returns Text starting with data:image/svg+xml, or BLANK when the ratio is BLANK
    FUNCTION Svg.ProgressBar = (
            ratio : SCALAR VARIANT VAL,
            barColor : SCALAR STRING VAL,
            trackColor : SCALAR STRING VAL
        ) =>
        VAR _width = MIN ( MAX ( ratio, 0 ), 1 ) * 100
        RETURN
            IF (
                NOT ISBLANK ( ratio ),
                "data:image/svg+xml;utf8,"
                    & "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 10' width='100' height='10'>"
                    & "<rect width='100' height='10' rx='2' fill='" & trackColor & "'/>"
                    & "<rect width='" & FORMAT ( _width, "0.0", "en-US" )
                    & "' height='10' rx='2' fill='" & barColor & "'/>"
                    & "</svg>"
            )
```

```dax
SVG Net Sales vs Target =
// WHAT: Progress of net sales against the target, as a bar.
// HOW: Svg.ProgressBar of [Net Sales] / [Sales Target]; colors from the report theme.
// NOTE: set the data category to Image URL.
Svg.ProgressBar ( DIVIDE ( [Net Sales], [Sales Target] ), "%231F4E79", "%23E6E6E6" )
```
