# Switches (disconnected tables)

One page, several views: instead of duplicating pages, the user picks the view with a small button slicer. How it works:

1. a **small options table** with no relationship to the model (disconnected table);
2. a **slicer** on that table, *Buttons* style, with **single select** and **force selection** turned on;
3. **measures** that read the option with `SELECTEDVALUE`;
4. **visuals, titles and colors** that use those measures.

Prefer a **field parameter** when the only need is to change the measure or the axis of a visual; prefer a **disconnected table** when the logic, the titles or the colors must follow the choice.

Always give `SELECTEDVALUE` a **default value** (case where nothing is selected). Show the DAX to the user **before** applying it.

## Comparison: Plan or PY

```dax
Param_Comparison =
DATATABLE (
    "Comparison", STRING,
    "SortOrder", INTEGER,
    { { "Plan", 1 }, { "PY", 2 } }
)
```

(Sort `Comparison` by `SortOrder`; hide `SortOrder`.)

```dax
// WHAT: reference value chosen by the user (Plan or PY).
// HOW: reads Param_Comparison; PY by default.
// NOTE: [Sales Target] is defined in base-measures.md, [Net Sales PY] in time-intelligence.md.
Net Sales Comparison =
SWITCH (
    SELECTEDVALUE ( Param_Comparison[Comparison], "PY" ),
    "Plan", [Sales Target],
    "PY", [Net Sales PY]
)
```

```dax
Net Sales Variance vs Comparison =
VAR _actual = [Net Sales]
VAR _reference = [Net Sales Comparison]
RETURN
    IF ( NOT ISBLANK ( _actual ) && NOT ISBLANK ( _reference ), _actual - _reference )
```

```dax
Net Sales Achievement % =
DIVIDE ( [Net Sales], [Net Sales Comparison] )
```

Dynamic title (visual title → *fx* → this measure):

```dax
Trend Title =
VAR _reference = SELECTEDVALUE ( Param_Comparison[Comparison], "PY" )
VAR _achievement = [Net Sales Achievement %]
RETURN
    "Are we above " & IF ( _reference = "Plan", "plan", "prior year" ) & "? "
        & IF ( _achievement >= 1, "Yes", "No" ) & ", "
        & FORMAT ( _achievement, "0.0%" )
```

Conditional color (formatting → *fx* → field value):

```dax
Variance Color =
IF ( [Net Sales Variance vs Comparison] >= 0, "#2E7D32", "#C62828" )
```

The two hex codes are placeholders: take the colors from the report theme (see `powerbi-report-design`).

## Ranking: Top or Bottom

```dax
Param_Direction =
DATATABLE ( "Direction", STRING, { { "Bottom" }, { "Top" } } )
```

```dax
// WHAT: rank of the customer by variance, in the chosen direction (5 worst or 5 best).
// HOW: RANKX over the visible customers; ignores customers without a variance.
// NOTE: Bottom by default; ties share the same rank (DENSE).
Variance Rank =
VAR _direction = SELECTEDVALUE ( Param_Direction[Direction], "Bottom" )
VAR _customers =
    FILTER (
        ALLSELECTED ( Dim_Customer[Customer] ),
        NOT ISBLANK ( [Net Sales Variance vs Comparison] )
    )
RETURN
    IF (
        ISINSCOPE ( Dim_Customer[Customer] ) && NOT ISBLANK ( [Net Sales Variance vs Comparison] ),
        IF (
            _direction = "Top",
            RANKX ( _customers, [Net Sales Variance vs Comparison],, DESC, DENSE ),
            RANKX ( _customers, [Net Sales Variance vs Comparison],, ASC, DENSE )
        )
    )
```

On the table: visual filter `Variance Rank` *is less than or equal to* 5, sorted by `Variance Rank` ascending.

Title:

```dax
Ranking Title =
"Which customers are the furthest "
    & IF ( SELECTEDVALUE ( Param_Direction[Direction], "Bottom" ) = "Top", "above", "below" )
    & " the reference?"
```

## View: Monthly or Cumulative

```dax
Param_View =
DATATABLE (
    "View", STRING,
    "SortOrder", INTEGER,
    { { "Monthly", 1 }, { "Cumulative", 2 } }
)
```

```dax
Net Sales View =
SWITCH (
    SELECTEDVALUE ( Param_View[View], "Monthly" ),
    "Monthly", [Net Sales],
    "Cumulative", [Net Sales YTD]
)
```

Same principle for the reference: `Net Sales Comparison View` returns `[Net Sales Comparison]` in the monthly view and its cumulative counterpart (`[Net Sales YTD PY]` for PY) in the cumulative view.

## Pitfalls

- A disconnected table must **never** receive a relationship.
- Without "force selection", several options can be ticked: `SELECTEDVALUE` then returns the default value.
- Name the tables `Param_...` and hide them from the report except the column used by the slicer.
