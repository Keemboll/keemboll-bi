# Parity, cut-over and retirement

Test mechanics (query files, `tests/ACCEPTANCE.md`, RLS protocol) are owned by `powerbi-testing`; this page says **what** to test for a migration and how to switch users over.

## Parity test plan

For each kept asset, in `tests/` and referenced from `MIGRATION.md`:

| Test | Expected value from | Grain |
|---|---|---|
| Row counts per table and period | Source system or old asset | month × entity |
| Control totals of each base measure (`[Net Sales]`, quantities) | Old asset, same filters | finest useful grain (e.g. month × store × category) |
| Each migrated calculation (LOD, set analysis, worksheet rule) | Old asset, same filters | grain of the visual that shows it |
| Calculations under the filters users actually apply | Old asset with the same selections | per filter combination listed in `MIGRATION.md` |
| Edge cases: empty period, missing previous year, division by zero, multi-select | Old asset | — |
| RLS equivalence: each source security rule gives the same visible scope | Source rule description | per role, plus "no access" user |
| Paginated: rows, totals, page breaks, PDF output | Old report | per report |

- Compare at the **finest useful grain**: a correct grand total can hide two errors that cancel out.
- **Tolerance**: zero on counts; on amounts, the rounding tolerance of `powerbi-testing` (level 2). A larger gap explained by a known rounding difference between the two tools is an accepted difference, written in `MIGRATION.md` and approved by the owner.
- **Accepted differences** are documented in `MIGRATION.md` (section 5) with their cause and the function that accepted them. Typical legitimate causes: the old tool was wrong (raise immediately, rule 2), different cut-off time, rounding at a different step, a filter that was invisible in the old tool.
- No values in the repository: record *passed / failed* and the order of magnitude of a gap (`powerbi-testing`).

## Parallel run

- **Default: two reporting cycles** (e.g. two month-end closes), both assets live, the old one **frozen** (read-only, no new development).
- During the run, the parity tests are re-run after each refresh of both sides; any new gap is analysed before the next cycle.
- Exit: no unexplained gap over the last cycle, owner sign-off in `tests/ACCEPTANCE.md`.

## Communication

| When | Message | To |
|---|---|---|
| Before the parallel run | What changes, why, where the new report is, dates, who to ask | All users of the asset |
| Start of the parallel run | Link to the new report, known differences (in business words), how to report a gap | Users |
| Cut-over date | Old asset becomes read-only / redirected; date of removal | Users |
| Retirement | Old asset removed; archive location for audit requests (by function) | Users, owner, IT |

Explain interaction differences (e.g. Qlik selections, Tableau actions) in the first message: they are the main source of "it is wrong" reports.

## Redirect and rollback

- Redirect: replace links in portals, bookmarks, e-mails and subscriptions; publish the new report in an app (`powerbi-governance`).
- **Rollback plan written before cut-over**: until retirement, the old asset can be reopened (unfrozen) if a blocking gap appears. State who decides and how fast.
- After retirement there is no rollback to the old tool: retirement waits until the owner confirms.

## Retirement checklist

- [ ] Parity signed and parallel run closed.
- [ ] Old asset archived (definition and, if required by retention rules, outputs) — location recorded by function.
- [ ] Access removed for users; old refresh schedules and subscriptions disabled.
- [ ] Nothing still points to the old asset (links, embedded pages, downstream extracts, other reports).
- [ ] Source connections, gateways entries and service accounts used only by the old asset identified for decommissioning (`powerbi-operations`).
- [ ] Licences of the old tool flagged to whoever manages them.
- [ ] `MIGRATION.md` updated: asset `retired`, date.
- [ ] Remaining improvements recorded in `DEBT.md` (`powerbi-lean`).
