# Migration checklist: Import → Direct Lake

Stated **at the time of writing — check the current documentation**: [Direct Lake overview — considerations and limitations](https://learn.microsoft.com/fabric/fundamentals/direct-lake-overview#considerations-and-limitations), [Direct Lake in Power BI Desktop](https://learn.microsoft.com/fabric/fundamentals/direct-lake-power-bi-desktop).

Plan the migration as a change (`C-001` in `CHANGES.md`) and get **user approval** before switching reports to the new model.

## 1. Inventory the Import model

- [ ] Tables, row counts, data sources, refresh duration and schedule.
- [ ] Power Query logic per table (joins, filters, derived columns, type changes) → each step must move upstream.
- [ ] Calculated columns and calculated tables → move upstream as Delta columns or tables. Keep calculation groups and field parameters (supported).
- [ ] Incremental refresh and model partitions → not available on Direct Lake tables; partition the Delta table instead, if needed.
- [ ] User-defined aggregations, hybrid tables → not supported on Direct Lake tables.
- [ ] Auto date/time or relationships on datetime columns → replace with a physical `Dim_Date` and date-only keys.
- [ ] Security roles (`RLS_Region`), connection identity, workspace roles of consumers → see the security section of `SKILL.md`.
- [ ] MDX clients (Analyze in Excel): user-defined hierarchies on Direct Lake tables and session-scoped MDX are not supported.
- [ ] Gateways: Direct Lake supports only cloud connections, no gateway.

## 2. Prepare the gold layer

- [ ] One Delta table per model table, with the logic moved from Power Query and calculated columns.
- [ ] [delta-table-checklist.md](delta-table-checklist.md) passed (types, V-Order, row groups, guardrails).
- [ ] Source in the same region as the workspace of the model (or a shortcut from a lakehouse in the model's region).

## 3. Build the Direct Lake model

- [ ] New model on Direct Lake on OneLake, in a development workspace; Import model left untouched.
- [ ] Measures copied unchanged; names unchanged so that reports rebind without edits.
- [ ] Tables that cannot move (Excel budget, mapping maintained by the business) added in Import as a composite model.
- [ ] Refresh behaviour chosen (automatic updates or explicit reframe), owner's read access checked.

## 4. Test parity and performance

- [ ] Run the non-regression queries of `powerbi-testing` on both models; same results for every `T-001`… test, including per role.
- [ ] No fallback or guardrail error (`EVALUATE TABLETRAITS()` on the SQL flavour; no query error on OneLake).
- [ ] Performance baseline with `powerbi-performance`: cold and warm timings of the main pages, compared with Import.
- [ ] Security tested with a Viewer account (model roles are not enforced for workspace Contributors and above).

## 5. Switch and roll back

- [ ] Rebind the reports to the new model (`powerbi-alm`), one report first, then the rest.
- [ ] Keep the Import model and its refresh **running in parallel** until parity is signed off; rollback = rebind the reports to the Import model.
- [ ] Version history of the model is available when live editing; it is not a substitute for the parallel Import model.
- [ ] Converting a Direct Lake table back to Import in web modeling is possible but **irreversible** for that table (it becomes an Import table reading the SQL endpoint).
- [ ] Retire the Import model once signed off; record it in `RELEASE_NOTES.md`.

## Direct Lake on SQL → Direct Lake on OneLake

Microsoft documents a migration through TMDL view (change the shared expression from `Sql.Database(...)` to `AzureStorage.DataLake(...)`, then refresh). It is not recommended when the model uses SQL endpoint views. Follow the current steps in [Direct Lake in Power BI Desktop](https://learn.microsoft.com/fabric/fundamentals/direct-lake-power-bi-desktop#migrate-direct-lake-on-sql-semantic-models-to-direct-lake-on-onelake) and take a version first.
