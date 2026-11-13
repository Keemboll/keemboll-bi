# Semantic model review checklist

To run through before publishing or during an audit. Report each deviation with: object, rule, proposed fix. If the project has a `TEAM_RULES.md`, read it first: a team rule replaces the matching default below.

## Model

- [ ] Star schema: each fact table linked to its dimensions in 1→* (see `powerbi-data-modeling`).
- [ ] No unjustified bidirectional relationship.
- [ ] No unjustified many-to-many relationship.
- [ ] `Dim_Date` present, continuous, marked as the date table; Auto date/time turned off.
- [ ] No calculated column that could be done in Power Query or at the source.
- [ ] Unused columns removed.

## Naming and presentation

- [ ] `Fact_` / `Dim_` / `_Measures` prefixes respected.
- [ ] Keys and technical columns hidden.
- [ ] Measures grouped in display folders.
- [ ] All visible measures have a description and a format.
- [ ] `Sort by column` set for month labels, days, ordered categories.
- [ ] `Summarize by = None` on non-additive numeric columns.

## DAX

- [ ] `DIVIDE` used for all divisions.
- [ ] No `FILTER(<whole table>)` in `CALCULATE` when a column filter is enough.
- [ ] No `IFERROR`.
- [ ] Base measures reused (no duplicated logic).
- [ ] Non-trivial measures carry the `// WHAT:` / `// HOW:` / `// NOTE:` comment header.
- [ ] Time intelligence based on `Dim_Date` (see `powerbi-dax-library`).

## Security

- [ ] RLS roles tested.
- [ ] No secret in parameters or M expressions.
- [ ] Sensitivity label applied (default; see the team rules).

## Example of a compliant measure

```dax
/// Gross margin as a percentage of net sales. Source: Fact_Sales.
Gross Margin % =
VAR _sales = [Net Sales]
VAR _margin = [Gross Margin]
RETURN
    DIVIDE ( _margin, _sales )
```

(The `///` comment only counts as a description in TMDL; in Power BI Desktop, fill in the **Description** property.)
