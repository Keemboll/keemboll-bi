---
name: powerbi-dax-udf
description: "DAX user-defined functions (UDFs): decide when logic belongs in a function rather than a measure, calculation group, field parameter or visual calculation, then name, type, document, store (functions.tmdl), test and version the function. Use when the same DAX logic is copied across several measures, when writing or reviewing a FUNCTION in a DAX query or in TMDL, when refactoring duplicated measures into a shared function, when importing third-party functions (DAX Lib), or when a model must move to compatibility level 1702 for UDFs. Triggers: UDF, user-defined function, DAX function, FUNCTION, DEFINE FUNCTION, functions.tmdl, reusable DAX, DAX library, daxlib, DAX Lib, refactor measures, duplicated logic, parameter type, VAL, EXPR, MEASUREREF, COLUMNREF, compatibility level 1702."
---

# DAX user-defined functions

A UDF packages **logic** once; measures keep the **meaning**. Apply `powerbi-conventions` (approval, naming of the calling measures), `powerbi-tmdl` (file editing), `powerbi-testing` (proof) and `powerbi-dax-library` (the formulas themselves). Syntax and limits: Microsoft page [DAX user-defined functions](https://learn.microsoft.com/dax/best-practices/dax-user-defined-functions) — generally available since the June 2026 release, compatibility level **1702** or higher. Re-check that page for anything that moves (IntelliSense, live connection, composite models).

## When to use a function

| Need | Use | Why |
|---|---|---|
| Same logic applied to several measures, columns or values (safe % change, YoY of any measure, banding, working days, SVG builder) | **UDF** | One definition, parameterized |
| A business KPI (`[Net Sales Change %]`) | **Measure** that calls the UDF | Keeps description, format, display folder, `KPI.md` entry |
| Composing two KPIs (`[Gross Margin] = [Net Sales] - [Cost]`) | **Measure** | Nothing to parameterize |
| The user switches the same transformation over any measure in a visual | **Calculation group** (`CG_*`) | Selected at report time, not author time |
| The user picks which measure or column a visual shows | **Field parameter** (`Param_*`) | A report-side choice |
| Logic that only depends on the fields of one visual (running sum on the axis) | **Visual calculation** (`powerbi-dax-library`) | No model object needed |

Rule of thumb: if two measures differ only by the measure or column they act on, extract a function. If a formula is used once, keep a measure.

## Naming (default of this skill)

- **Namespace by domain**, separated by periods, then PascalCase: `Ratio.PctChange`, `Period.YoYPct`, `Fmt.Compact`, `Svg.ProgressBar`, `Band.ABC`.
- Name what the function returns; start with a verb only when it performs an action (`Fmt.ToText`).
- Avoid a namespace that is itself a DAX function name (`Time`, `Date`, `Format`): it reads like a call to the built-in.
- Parameters in **camelCase**, no periods (rule of the engine): `metric`, `dateColumn`, `barColor`.
- The engine requires unique names, letters, digits and underscores, periods only between segments, no clash with built-in functions or reserved words.
- Measures that call a function follow `powerbi-conventions` as any measure.

## Rules

1. Every function has a `///` block above it: one sentence, then `@param {Type} name - description` for each parameter and `@returns`. Only `///` lines show in IntelliSense; `//` and `/* */` do not.
2. **Explicit type and passing mode** on every parameter (`SCALAR VARIANT VAL`, `SCALAR NUMERIC EXPR`, `COLUMNREF`). For a measure value that can be BLANK, prefer `VARIANT`: a numeric subtype casts the argument, and the BLANK case must be tested either way.
3. **No business constants inside a function** (thresholds, rates, colors, dates): they are parameters, and the calling measure takes them from `KPI.md` or the theme.
4. **No hidden dependency** on a table, column or report filter: pass columns and measures as parameters. A function that reads a model object directly says so in its description.
5. **Test before saving to the model**: a `DEFINE FUNCTION ... EVALUATE` query with known cases, including BLANK, zero and a multi-selection (template in [references/tmdl-and-testing.md](references/tmdl-and-testing.md)).
6. Refactoring measures into a function is a **non-regression** case (`powerbi-testing`, level 4): same query before and after, identical values.
7. Raising the compatibility level to 1702 is a **model change that needs approval**. Upgrading a compatibility level is **irreversible**. Check first that the deployment target, the deployment pipeline and every external tool used on the model accept that level.
8. Third-party functions (for example DAX Lib packages from daxlib.org, or any installer it offers) are a dependency: read the code, pin the version, record source and version in `DATA_DICTIONARY.md`, and test them like your own.
9. Object-level security does not carry over to functions: a function name or description never reveals a secured object.

## Evaluation context: value or expression

The passing mode decides **when** an argument is evaluated:

- `VAL` (default for `SCALAR`, `TABLE`, `ANYVAL`): evaluated **once, before** the call, in the caller's filter and row context. Inside the function it is a constant; `CALCULATE` cannot change it.
- `EXPR` (mandatory for `ANYREF`, `COLUMNREF`, `MEASUREREF`, `TABLEREF`, `CALENDARREF`): evaluated **inside** the function, each time it is referenced, in the function's filter context. It inherits the caller's filter context but **not** its row context.

```dax
DEFINE
    /// Wrong for time intelligence: metric is already a number
    FUNCTION Period.PriorYearVal = ( metric : SCALAR NUMERIC VAL, dateColumn : COLUMNREF ) =>
        CALCULATE ( metric, SAMEPERIODLASTYEAR ( dateColumn ) )
    /// Right: metric is re-evaluated under the shifted dates
    FUNCTION Period.PriorYearExpr = ( metric : SCALAR NUMERIC EXPR, dateColumn : COLUMNREF ) =>
        CALCULATE ( metric, SAMEPERIODLASTYEAR ( dateColumn ) )

EVALUATE
SUMMARIZECOLUMNS (
    Dim_Date[Year],
    "Net Sales", [Net Sales],
    "PY (val)", Period.PriorYearVal ( [Net Sales], Dim_Date[Date] ),
    "PY (expr)", Period.PriorYearExpr ( [Net Sales], Dim_Date[Date] )
)
```

`PY (val)` repeats the current year; `PY (expr)` returns the prior year. Use `EXPR` whenever the function changes filter context; use `VAL` for plain arithmetic and for row values in calculated columns or iterators.

## Process

1. **Inventory** duplicated logic with `powerbi-lean` (`audit`, then a read of near-duplicates).
2. **Propose** the functions: name, parameters, measures that will call them, compatibility level impact. **Wait for approval** (`powerbi-conventions`).
3. **Test** each function in a query before it enters the model (rule 5).
4. **Write** it in `definition/functions.tmdl` following `powerbi-tmdl`, or save it from the DAX query view.
5. **Rewire** the measures one by one; run the non-regression query (rule 6).
6. **Record**: a "Functions" section in `DATA_DICTIONARY.md` (name, purpose, parameters, callers, source and version if third-party) and a `C-xxx` entry in `CHANGES.md`.

## Limits that shape the design

At the time of writing (re-check the Microsoft page): no display folders, no hiding and no translations for functions; no recursion and no overloading; no explicit return type; parameter descriptions are not a model property (hence the `@param` lines); a visual calculation can only pass fields present in the visual; model measures in a composite model cannot call functions of the source model.

## References

- [references/patterns.md](references/patterns.md) — six ready-to-use functions with their calling measures.
- [references/tmdl-and-testing.md](references/tmdl-and-testing.md) — `functions.tmdl` form, test query template, INFO queries, migration checklist.
