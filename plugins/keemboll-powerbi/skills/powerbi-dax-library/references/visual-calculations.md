# Visual calculations

A visual calculation is DAX defined **on a visual**, not in the model. It works on the visual matrix (the aggregated data already shown), can refer to the fields, measures and other visual calculations of that visual, and knows its structure (rows, columns, levels).

Functions, supported visuals and limits evolve: check <https://learn.microsoft.com/power-bi/transform-model/desktop-visual-calculations-overview> before relying on a detail. **The examples below were not executed.**

## Visual calculation or model measure

| Need | Where |
|---|---|
| Running total, moving average, variance versus the previous row, on the axis of this visual | Visual calculation |
| Rank within the visual, % of parent or of grand total on the visual's own hierarchy | Visual calculation |
| Business KPI (listed in `KPI.md`), or anything reused in several visuals or reports | Model measure |
| Logic needed in a filter, a slicer, an export or a row-level security rule | Model measure |
| Logic that depends on relationships (`USERELATIONSHIP`, `RELATED`) | Model measure |

Rule of thumb: **presentation logic local to one visual** is a visual calculation; everything else is a measure.

## Consequences

- Visual calculations are stored in the **report** (visual definition in PBIR), not in the semantic model: they do not appear in the data dictionary and are not model objects.
- They cannot be reused or copied to another visual: a field inventory such as `lean.py usage` (skill `powerbi-lean`) run on other visuals will not show them. Duplicating the same visual calculation in several visuals is the signal to move it to a model measure.
- A field must be on the visual (possibly hidden) before a visual calculation can refer to it.
- Document a non-obvious visual calculation in `REPORT.md` (see `powerbi-documentation`).

## Examples

On a matrix with `Dim_Date[Year]` and `Dim_Date[Month]` on rows and `[Net Sales]` as value. Inside a visual calculation, fields are referenced by their name on the visual.

```dax
Running Net Sales = RUNNINGSUM ( [Net Sales], HIGHESTPARENT )
```

(restarts at each year, the highest level of the axis)

```dax
Net Sales Moving Average = MOVINGAVERAGE ( [Net Sales], 3 )
```

```dax
Net Sales vs Previous = [Net Sales] - PREVIOUS ( [Net Sales] )
```

```dax
Share of Parent = DIVIDE ( [Net Sales], COLLAPSE ( [Net Sales], ROWS ) )
```

```dax
Share of Grand Total = DIVIDE ( [Net Sales], COLLAPSEALL ( [Net Sales], ROWS ) )
```

```dax
Rank in Visual = RANK ( DENSE, ORDERBY ( [Net Sales], DESC ) )
```

Other functions: `EXPAND` / `EXPANDALL` (evaluate at a lower level), `FIRST`, `LAST`, `NEXT`, `RANGE`, `LOOKUP`, `ISATLEVEL`. The optional axis argument (`ROWS`, `COLUMNS`, `ROWS COLUMNS`...) sets the direction of traversal; the optional reset argument (`NONE`, `HIGHESTPARENT`, `LOWESTPARENT`, a level number or a column) sets where a running calculation restarts.

## Pitfalls

- Model time intelligence functions (`DATEADD`, `TOTALYTD`...) are discouraged inside visual calculations: use `PREVIOUS`, `RUNNINGSUM` and the reset argument.
- The result depends on the layout: changing the axis fields or their order changes the numbers.
- Limits listed by the documentation at the time of reading (to be confirmed): not available on slicers, custom visuals and some AI or script visuals; the results cannot be used to filter or sort; no dynamic format string; data export excludes them.
- Test like any other figure shown to users (`powerbi-testing`): the visual calculation is checked in the report, not with a DAX query on the model.
