# What `lean.py audit` checks

The "Category" column is the label printed by the script.

| Priority | Category | Rule |
|---|---|---|
| 1 | Duplicate | Measures whose DAX is identical once comments and whitespace are removed (case-insensitive; expressions of 12 characters or fewer are ignored) |
| 1 | Model | No table marked as a date table (`dataCategory: Time`) |
| 2 | Unused | Measure used neither by the report, nor by a used measure, a role, a calculation group, a calculated table or a dynamic format string |
| 2 | Unused | Column not used (report, DAX, relationships, sort-by columns, hierarchy levels used by the report, key of the date table) — measure tables excluded |
| 2 | DAX | `FILTER` applied directly to a table of the model |
| 2 | Hardcoded value / risk | `TODAY()` / `NOW()` / `UTCTODAY()` / `UTCNOW()`; `IFERROR` / `ISERROR` |
| 2 | Model | `summarizeBy: sum` on a column whose name looks like an identifier, a code or a period (`id`, `key`, `code`, `year`, `month`, `quarter`, `num`, `no`, `number`) |
| 3 | Hardcoded value / risk | `DATE(yyyy, …)`; column of a **related** table compared (`=`, `<>`, `IN`) to a number (two digits or more), a label or a list; division `/` by an expression instead of `DIVIDE` |
| 3 | Documentation | Visible measure without a description; without a format (measures containing a string literal are skipped, as they probably return text) |
| 3 | Model | Visible foreign key (the "many" side column of a relationship) |
| 3 | Structure | Table without a relationship (often expected: parameter, disconnected table) — calculation groups and measure tables excluded |

A measure table is a table that holds measures and whose columns are all hidden.

## How "used" is computed

1. Starting point: every field referenced in the JSON files of the report (visuals, visual, page and report filters, bookmarks, conditional formatting), the columns of relationships, RLS roles, calculation groups, calculated tables (including field parameters) and the key column (`isKey`) of the date table.
2. Propagation: a used measure makes the measures and columns of its DAX (and of its dynamic format string) used; a used column makes its sort-by column and the DAX of a calculated column used.

## `lean.py catalog`

Same reading of the model and same usage computation, rendered as a data dictionary (tables, columns, measures and their DAX, relationships, roles, visible objects without a description) on standard output; nothing is written to disk. E-mail addresses are masked everywhere (descriptions, DAX of measures) and the filter of a role that contains one is not copied. **Only e-mail addresses** are: a hardcoded person name or `DOMAIN\account` identifier is copied — flag it (`powerbi-governance`). OLS is not rendered. The table type is derived from the prefixes of `powerbi-conventions` (`Fact_`, `Dim_`, `_Measures`, `Param_`, `CG_`), or from the presence of a calculation group; empty otherwise. Usage: skill `powerbi-documentation`.

## Limits

- **One report only**: reports connected to the published model, Excel workbooks and external queries are not visible.
- The DAX rules (duplicates, hardcoded values, `FILTER`, division) scan **measures** only, and each of the date / `IFERROR` / division rules reports its first match per measure.
- Unqualified DAX references `[X]` are attached to a measure when a measure has that name.
- A column used only as a level of a model hierarchy that the report does not use is reported as unused.
- `--changed` filters **by file** (files changed since the last commit, plus untracked files): every finding of a changed table is shown, and model-wide findings (no date table) are dropped. Without a Git repository, the full analysis runs.
- Duplicate detection is **exact** (after normalisation): near-duplicates need a human read.
- The "hardcoded value" and "identifier" heuristics are signals to confirm, not certain errors.
