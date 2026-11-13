# Power Query review checklist

Tick each item per query; report failures in the review table (query / step / finding / proposal). Naming of model tables and the approval step: `powerbi-conventions`.

## Organisation

- [ ] Loaded queries named as the model table (`Fact_Sales`, `Dim_Customer`).
- [ ] Staging queries prefixed `stg_`, load disabled.
- [ ] Parameters prefixed `p` or in the `Parameters` group; functions prefixed `fn`.
- [ ] Query groups in place (`Parameters`, `Functions`, `Staging`, `Dimensions`, `Facts`).
- [ ] No default step names (`#"Changed Type1"`, `#"Custom1"`); one step = one intention.
- [ ] Non-obvious steps commented with the reason.
- [ ] No orphan query (neither loaded nor referenced).

## Sources and parameters

- [ ] Server, database, path, environment come from parameters; nothing hard-coded.
- [ ] No credential, key or token anywhere in M or parameters.
- [ ] Native SQL replaced by a source view where possible; otherwise `Value.NativeQuery` with `EnableFolding = true` when the connector supports it.
- [ ] Privacy levels set; no `Formula.Firewall` workaround based on *Ignore privacy levels*.
- [ ] On-premises sources identified and covered by a gateway.

## Folding and performance

- [ ] Row filters and column selection are the first steps after navigation.
- [ ] Last step of each heavy query checked for folding (method noted).
- [ ] Non-foldable steps placed last, on a reduced table, or moved upstream.
- [ ] `Table.Buffer` only with a measured reason.
- [ ] Heavy queries not referenced many times without measurement.
- [ ] Helper queries not loaded.

## Typing and quality

- [ ] Every loaded column has an explicit type; no `any` column.
- [ ] Types set once, at the end of staging; text → date/number conversions pass a culture.
- [ ] Money as fixed decimal (`Currency.Type`), keys as `Int64.Type`.
- [ ] Date and time split; unneeded precision removed.
- [ ] Text keys trimmed and cleaned; null handling explicit.
- [ ] `try ... otherwise` only for a documented business fallback.
- [ ] Rejected-row count available to tests (`powerbi-testing`).

## Incremental refresh (if used)

- [ ] `RangeStart` / `RangeEnd` exist, exact names, type Date/Time.
- [ ] Filter has exactly one inclusive bound.
- [ ] Filter folds (method noted).
- [ ] Policy decisions written down with their reason.
- [ ] Deployment path does not republish over the partitions (`powerbi-alm`).

## After applying

- [ ] Refresh succeeds in the development workspace.
- [ ] Row counts and key totals (`[Net Sales]`) reconciled with the source (`powerbi-testing`).
- [ ] Refresh time before / after recorded.
