# Query folding

Microsoft references: [Power Query query folding](https://learn.microsoft.com/power-query/power-query-folding) and [Query folding guidance in Power BI Desktop](https://learn.microsoft.com/power-bi/guidance/power-query-folding). Folding support differs by connector and changes over time: what follows are tendencies to check, not guarantees.

## How to check

| Method | Where | What it tells |
|---|---|---|
| *View Native Query* (right-click a step) | Power Query in Desktop | Available = the step folds into the shown query. Greyed out = does not fold, **or** the connector cannot show it (not proof either way) |
| Step folding indicators | Power Query Online (dataflows, some editors) | Per-step status: folded, not folded, unknown |
| *Query diagnostics* | Power Query in Desktop, *Tools* tab | Queries actually sent to the source and time spent per step |
| Source-side trace | SQL Profiler, Extended Events, the source's query log | What the source really received — the definitive answer |

Check the **last** step of each heavy query: folding that stops at step 3 of 10 means steps 4–10 run on every row returned by step 3.

## Steps that typically break folding

- A custom function applied row by row (`Table.TransformColumns` or `Table.AddColumn` calling `fn...`).
- `Table.Buffer`, `List.Buffer`.
- Index columns (`Table.AddIndexColumn`).
- Merges or appends across **different sources** (or across privacy boundaries).
- Some type conversions and text functions the connector cannot translate (culture-specific conversions, `Text.Proper`, `Text.Clean` on many connectors).
- Complex custom columns (record or list logic, `try ... otherwise`).
- Pivot / unpivot, `Table.Distinct` on some connectors, transposition.
- Steps after a non-folding step: once folding stops, nothing after it folds.

## Ordering rule

1. Navigation (`Source{[Schema = ..., Item = ...]}[Data]`).
2. Row filters (including `RangeStart` / `RangeEnd`).
3. Column selection (`Table.SelectColumns`, rather than `Table.RemoveColumns`, so that a new source column is not loaded by surprise).
4. Foldable joins, groupings and type changes.
5. Non-foldable steps last, on the reduced table.

When a non-foldable step is needed on a large table, move it upstream (view, dataflow) rather than accept a full read at each refresh.

## Native SQL

When the logic can only be expressed in SQL, `Value.NativeQuery` with `EnableFolding = true` lets later steps fold on top of the native query for connectors that support it (SQL Server and some others — check the connector documentation).

```powerquery
let
    Source = Sql.Database(pServer, pDatabase),
    ActiveSales = Value.NativeQuery(
        Source,
        "SELECT OrderDate, DeliveryDate, CustomerKey, ProductKey, StoreKey, Quantity, NetAmount FROM dbo.FactSales WHERE IsDeleted = 0",
        null,
        [EnableFolding = true]
    ),
    #"Kept refresh window" = Table.SelectRows(
        ActiveSales,
        each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd
    )
in
    #"Kept refresh window"
```

- Prefer a view at the source to SQL text in the model: reviewable, versioned with the database, reusable.
- Never build SQL by concatenating user-visible values; parameters for the native query go in the third argument when the connector supports it.
- A native query may require approval in Desktop on first run; that prompt is a security feature, not a nuisance to disable.
