# Incremental refresh

Microsoft references, to re-read before each new setup (limits and options move): [overview](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-overview), [configure](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-configure), [troubleshoot](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-troubleshoot), [advanced, XMLA endpoint](https://learn.microsoft.com/power-bi/connect-data/incremental-refresh-xmla).

## When

- A fact table whose full refresh is long or heavy (tens of millions of rows and more), with a reliable date or date/time column.
- Not for small tables, nor for dimensions (they change everywhere, not by date).
- Direct Lake tables have no Power Query partitions: see `powerbi-direct-lake`.

## Procedure

1. **Parameters**: create `RangeStart` and `RangeEnd` — exact names (case-sensitive), type **Date/Time**. Their current values only limit what loads in Desktop: choose a short recent window (a few days).
2. **Filter** the fact query on the date column, right after navigation: `each [OrderDate] >= RangeStart and [OrderDate] < RangeEnd`. Exactly one bound has `=`; with `=` on both, a row on the boundary lands in two partitions (duplicates). Pattern: [m-patterns.md](m-patterns.md#3-incremental-refresh-fact-query).
3. **Integer date key** at the source (`yyyymmdd`): keep the parameters Date/Time and convert them with a function (`fnDateKey`), not the column.
4. **Check folding** of the filter ([query-folding.md](query-folding.md)). Desktop warns when it cannot confirm folding; for non-SQL sources confirm with *Query diagnostics* or a source trace. In a pure Import policy a non-folding filter is applied locally after reading **all** rows for each partition: refresh gets slower, not faster.
5. **Policy** on the table (Desktop: table context menu → *Incremental refresh*; in TMDL the `refreshPolicy` of the table, see `powerbi-tmdl`).
6. **Publish**, then run the **first refresh manually** and monitor it (`powerbi-operations`): it loads the whole archive period and can take long.

## Policy decisions

| Setting | Question to answer | Default |
|---|---|---|
| Archive data starting … before refresh date | How much history do reports need? | 5 years |
| Incrementally refresh data starting … before refresh date | How far back can source rows still change (late entries, corrections)? | 10 days |
| Detect data changes | Is there a reliable last-modified date/time column, distinct from the partition column? | Off unless such a column exists |
| Only refresh complete days | Must partial days be excluded (refresh runs during the day)? | Off; forced on with real-time DirectQuery |
| Get the latest data in real time with DirectQuery | Is real time a requirement? (Premium / PPU / Embedded only; the whole query must fold) | Off |

Write the decisions and their reasons in the project documentation (`powerbi-documentation`).

## Pitfalls

- **Time zone**: the service computes "today" in UTC unless a refresh time zone is configured; refreshes not started by the service (e.g. XMLA/TMSL commands) use UTC. A refresh at 01:00 local time may still be "yesterday".
- **Deleted rows** are not detected by *Detect data changes*: only soft deletes (row kept, flagged, last-modified date updated). Hard deletes in the refresh window are handled by the refresh itself; older ones need a partition refresh or a full refresh.
- **Detect data changes column** is stored in the model: reduce its precision or follow the Microsoft guidance on custom polling queries.
- **Republishing from Desktop** replaces the published model and drops existing partitions and data; after publishing, the model cannot be downloaded back as `.pbix`. For later metadata changes use a metadata-only deployment (XMLA endpoint, deployment pipelines — check current support in the Microsoft documentation, and see `powerbi-alm`).
- **Single source**: all partitions of the table must query the same data source.
- **Same parameters for every table**: several tables with a policy share `RangeStart` / `RangeEnd`, each with its own periods.
- **Refresh time limits** differ between Pro and Premium/Fabric capacities and do not apply the same way to XMLA refreshes: check the current values in the Microsoft documentation; a long initial refresh can be bootstrapped through the XMLA endpoint.
- **Source timeout**: a source command timeout can be set in M (`Sql.Database ( pServer, pDatabase, [CommandTimeout = #duration ( 0, 2, 0, 0 )] )`); each partition query observes it.
- **Large semantic model storage format**: when the model may grow large on a capacity, enable it before the first refresh.
