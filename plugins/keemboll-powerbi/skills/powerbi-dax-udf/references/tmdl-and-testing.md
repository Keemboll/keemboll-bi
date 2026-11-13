# Storing and testing functions

Editing rules for TMDL files (tabs, synchronization with Power BI Desktop, Git): `powerbi-tmdl`. Test levels and the `tests/` folder: `powerbi-testing`.

## `functions.tmdl`

In a PBIP project, all the functions of the model live in one file: `<Name>.SemanticModel/definition/functions.tmdl`. Functions are direct children of the model, so the declaration starts at column 0, like `relationships.tmdl`:

- description lines `///` just above `function`;
- a name that contains a period is enclosed in single quotes (TMDL rule for names with `.`, `=`, `:`, `'` or spaces);
- a multi-line body starts on the line after `=` and is indented two tabs.

```tmdl
/// Relative change between two values; BLANK when either value is BLANK or the reference is zero.
/// @param {SCALAR VARIANT VAL} current - Value of the period being analyzed
/// @param {SCALAR VARIANT VAL} reference - Value it is compared to
/// @returns Ratio (0.15 = +15%), to format 0.0% in the calling measure
function 'Ratio.PctChange' = ( current : SCALAR VARIANT VAL, reference : SCALAR VARIANT VAL ) =>
		IF (
			NOT ISBLANK ( current ) && NOT ISBLANK ( reference ),
			DIVIDE ( current - reference, reference )
		)

/// Year-over-year change of any measure or scalar expression, through the date column passed.
/// @param {SCALAR NUMERIC EXPR} metric - Measure or expression to compare, evaluated inside the function
/// @param {COLUMNREF} dateColumn - Date column of the marked date table
/// @returns Ratio of change versus the same period last year; BLANK when either year is BLANK
function 'Period.YoYPct' = ( metric : SCALAR NUMERIC EXPR, dateColumn : COLUMNREF ) =>
		VAR _current = metric
		VAR _prior = CALCULATE ( metric, SAMEPERIODLASTYEAR ( dateColumn ) )
		RETURN
			Ratio.PctChange ( _current, _prior )
```

The quotes belong to TMDL only: in DAX, the body and every caller write `Ratio.PctChange ( ... )` without quotes (a quoted name in DAX is a table).

Do not write a `lineageTag` by hand: let Power BI Desktop generate it (`powerbi-tmdl`). In the TMDL view of Desktop, the same declaration goes under a `createOrReplace` line, indented one tab, then **Apply**.

The safest way to obtain the exact serialization of a function is to save it once from the DAX query view and read the `functions.tmdl` that Desktop writes; align the other functions on it.

## Test query template

One file per function in `tests/`, named per `powerbi-testing` (`T-0xx_<function>.dax`). The function is defined **in the query**, so the model is not changed. Each row is a case; the query returns zero rows when everything is right.

```dax
// WHAT: Ratio.PctChange returns the expected ratio and keeps BLANK.
// EXPECTED: zero rows.
DEFINE
    FUNCTION Ratio.PctChange = ( current : SCALAR VARIANT VAL, reference : SCALAR VARIANT VAL ) =>
        IF (
            NOT ISBLANK ( current ) && NOT ISBLANK ( reference ),
            DIVIDE ( current - reference, reference )
        )

    VAR _cases =
        DATATABLE (
            "Case", STRING,
            "Current", DOUBLE,
            "Reference", DOUBLE,
            "Expected", DOUBLE,
            {
                { "growth", 115, 100, 0.15 },
                { "decline", 80, 100, -0.2 },
                { "zero reference", 50, 0, BLANK () },
                { "blank current", BLANK (), 100, BLANK () },
                { "blank reference", 100, BLANK (), BLANK () }
            }
        )

EVALUATE
FILTER (
    ADDCOLUMNS ( _cases, "Actual", Ratio.PctChange ( [Current], [Reference] ) ),
    NOT ( ( ISBLANK ( [Actual] ) && ISBLANK ( [Expected] ) )
        || ABS ( [Actual] - [Expected] ) < 0.000001 )
)
```

For a function that takes a measure or a column (`EXPR`, `COLUMNREF`), test it in model context instead: compare it, period by period, to the formula of `powerbi-dax-library` it replaces.

```dax
// WHAT: Period.YoYPct gives the same result as the library formula.
// EXPECTED: zero rows.
DEFINE
    FUNCTION Ratio.PctChange = ( current : SCALAR VARIANT VAL, reference : SCALAR VARIANT VAL ) =>
        IF ( NOT ISBLANK ( current ) && NOT ISBLANK ( reference ), DIVIDE ( current - reference, reference ) )
    FUNCTION Period.YoYPct = ( metric : SCALAR NUMERIC EXPR, dateColumn : COLUMNREF ) =>
        VAR _current = metric
        VAR _prior = CALCULATE ( metric, SAMEPERIODLASTYEAR ( dateColumn ) )
        RETURN Ratio.PctChange ( _current, _prior )

EVALUATE
FILTER (
    SUMMARIZECOLUMNS (
        Dim_Date[Year],
        Dim_Date[MonthNum],
        "Before", [Net Sales Change %],
        "After", Period.YoYPct ( [Net Sales], Dim_Date[Date] )
    ),
    NOT ( ( ISBLANK ( [Before] ) && ISBLANK ( [After] ) )
        || ABS ( [Before] - [After] ) < 0.000001 )
)
```

Without a DAX engine available to the agent, hand these queries to the user and report them as "not executed" (`powerbi-testing`, rule 1).

## Inspecting the functions of a model

```dax
// Full metadata of the user-defined functions (needs write permission on the model).
EVALUATE INFO.USERDEFINEDFUNCTIONS ()
```

```dax
// Names and limited metadata, readable without write permission.
EVALUATE INFO.FUNCTIONS ( "ORIGIN", "2" )
```

In Power BI Desktop, functions also appear under the **Functions** node of the Model explorer, with quick queries to define and evaluate them in the DAX query view.

## Migration checklist: duplicated measures → function

1. [ ] `powerbi-lean` `audit` run; duplicated or near-duplicated measures listed with the part that varies (the measure, a column, a threshold).
2. [ ] Function signature written: name (namespace + PascalCase), typed parameters, passing mode chosen (`EXPR` if the function changes filter context).
3. [ ] Compatibility level checked in `database.tmdl`; if below 1702, the upgrade is approved, known to be irreversible, and accepted by the deployment target and the external tools in use.
4. [ ] Plan approved: function, measures rewired, measures unchanged (`powerbi-conventions`).
5. [ ] Backup commit; "before" values captured with a query on the measures concerned.
6. [ ] Function tested in a `DEFINE FUNCTION` query (cases, BLANK, zero, multi-selection).
7. [ ] Function added to `functions.tmdl` (or saved from the DAX query view).
8. [ ] Measures rewired one at a time; name, description, format and display folder unchanged, so reports keep working.
9. [ ] Non-regression query: "before" = "after" on every case.
10. [ ] `DATA_DICTIONARY.md` "Functions" section updated (name, purpose, parameters, callers, source and version if third-party); `C-xxx` entry in `CHANGES.md`.
