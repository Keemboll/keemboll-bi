---
name: powerbi-migration
description: "Migrate existing BI assets into a governed Power BI project: format migrations inside Power BI (PBIX to PBIP, model.bim / TMSL to TMDL, legacy report format to PBIR, splitting duplicated PBIX files into one shared model and thin reports), migrations from other tools (Excel and Power Pivot, Tableau, Qlik, SSRS / paginated, Looker, SSAS / AAS tabular) and platform moves announced by Microsoft. A method, not a converter: inventory, rationalise, map, rebuild, prove parity, cut over, retire, with exit criteria, concept mapping tables and the MIGRATION.md template. Load it when the starting point is not a clean PBIP project or comes from another tool, when planning a replatforming, a parallel run or a decommission. Triggers: migration, migrate, convert, PBIX to PBIP, PBIR, TMDL conversion, Tableau, Qlik, QlikView, Qlik Sense, Excel, Power Pivot, SSRS, paginated, Looker, SSAS, AAS, legacy report, replatform, parity, parallel run, cut-over, decommission, LOD, set analysis, thin report, shared model."
---

# powerbi-migration — move existing BI assets into a governed project

This skill is a **method**, not a converter. No tool turns a Tableau workbook, a Qlik app or an Excel model into a faithful Power BI report: the agent translates **intent, not syntax**, and proves equality with tests. Each step points to the skill that is authoritative for the work; this skill only says what to migrate, in which order, and when a step is finished.

## When to use it / not

- Use it: a `.pbix` to bring under version control; a project still in `model.bim` or the legacy report format; several PBIX files that each carry a copy of the same model; reports in Excel / Power Pivot, Tableau, Qlik, SSRS, Looker or SSAS / AAS to rebuild in Power BI; a platform move announced by Microsoft (see [Platform moves](#platform-moves)).
- Not for: taking over a PBIP project with no format change → `powerbi-project` (*Taking over an existing project*); cleaning a model → `powerbi-lean`; changing storage mode Import → Direct Lake → `powerbi-direct-lake`.

## Rules for the agent

1. **Never work on the only copy.** The source artefact (file, workbook, app, server export) is kept untouched and archived before anything else; all work happens on a copy.
2. **Migration ≠ redesign.** First reach parity; improvements go to `DEBT.md` (`powerbi-lean`) unless the user decides otherwise. Exception: a defect that would be reproduced knowingly (a wrong number, a broken rule) is **raised immediately** to the business owner, who decides whether to fix it or reproduce it.
3. **Do not migrate what nobody uses.** Inventory usage first; the **business owner** decides what is dropped, never the agent.
4. **No real data values** in `MIGRATION.md`, mapping documents or tests: object names, definitions and orders of magnitude only (`powerbi-testing`).
5. **Not done until proven.** A migrated report is finished when its parity tests pass and the owner signs `tests/ACCEPTANCE.md` (`powerbi-testing`).
6. **Credentials and connection strings are re-created in the target**, never copied into files, mapping documents or commits (`powerbi-governance`, `powerbi-alm`).
7. Apply `powerbi-conventions` before any write (approval, Git, existing model, confidentiality).

## The seven steps

| # | Step | Deliverable | Authoritative skill | Exit criterion |
|---|---|---|---|---|
| 1 | **Inventory** — assets, owners (by function), usage, refresh, sources, security, embedded logic | `MIGRATION.md` asset table | `powerbi-migration` | Every asset listed with usage and owner; source archived |
| 2 | **Rationalise** — keep / merge / retire; many reports → few shared models | Decision column filled in `MIGRATION.md` | `powerbi-migration`, `powerbi-project` | Each decision approved by the business owner |
| 3 | **Map** — source concept → Power BI concept, calculation by calculation | Mapping table; definitions in `KPI.md` | `powerbi-project` (`KPI.md`), mapping references below | Every kept calculation has a target and an approved definition |
| 4 | **Rebuild** — model, queries, measures, pages | `*.SemanticModel` (TMDL), `*.Report` (PBIR) | `powerbi-data-modeling`, `powerbi-power-query`, `powerbi-dax-library`, `powerbi-report-design` | Every mapped item implemented; `lean.py audit` without blocking finding |
| 5 | **Prove parity** — reconciliation at the finest useful grain, tolerance, accepted differences, RLS equivalence | `tests/`, parity section of `MIGRATION.md` | `powerbi-testing` | All parity tests pass or differences accepted in writing |
| 6 | **Cut over** — parallel run, communication, redirect, freeze the old asset | Cut-over plan and date | `powerbi-alm`, `powerbi-documentation` | Parallel run ended without blocking gap; users redirected; owner sign-off |
| 7 | **Retire** — archive, remove access, decommission schedule and licence | Retirement checklist ticked | `powerbi-operations`, `powerbi-governance` | Old asset read-only or removed; nothing still points to it |

Steps 3 to 5 run **per page or per model**, like the phases of `powerbi-project`: deliver one model with its reports to parity before starting the next.

Notes:

- **Step 3** — the business definition of each kept calculation goes to `KPI.md` (`powerbi-project`), status `implemented` but **to be confirmed**: an old formula is not an approved definition.
- **Step 4** — rebuild pages for Power BI's interaction model (cross-filtering, drillthrough, tooltips) rather than pixel-copying the source; mock up first with `powerbi-mockup` when the layout changes.
- **Step 5** — the expected value comes from the **source system or the old report**, never from the new measure. Default tolerance and parallel run: [references/parity-and-cutover.md](references/parity-and-cutover.md).
- **Step 6** — default parallel run: **two reporting cycles** (e.g. two month-end closes). The old asset is frozen (read-only) from the first day of the parallel run.

## Format migrations inside Power BI

- **PBIX → PBIP**, `model.bim` → TMDL, legacy report → PBIR: procedure, first commit and checks in [references/pbix-to-pbip.md](references/pbix-to-pbip.md). The first commit is the **unmodified** conversion, so that every later change shows in the diff.
- **Thin-report split**: several PBIX files carrying copies of the same model become one shared model plus reports connected to it. Same reference.

## Migrations from other tools

| Source | Reference | Biggest trap |
|---|---|---|
| Tableau | [references/mapping-tableau.md](references/mapping-tableau.md) | LOD expressions and filter order do not translate one to one |
| Qlik (QlikView, Qlik Sense) | [references/mapping-qlik.md](references/mapping-qlik.md) | Associative model: selections no longer propagate everywhere |
| Excel / Power Pivot, SSRS / paginated, Looker, SSAS / AAS | [references/mapping-excel-ssrs.md](references/mapping-excel-ssrs.md) | Manual inputs with no owner; forcing print reports into interactive pages |

Every DAX "equivalent" in these references is a **pattern to test, not a guaranteed equivalent**: it is accepted only once a parity test passes.

## Platform moves

Microsoft announces retirements and default-format changes that owners must plan for. The agent states the change, points to the Microsoft documentation and adds an entry to `MIGRATION.md`; it does not assert a date it has not checked.

- **PBIR becomes the report format**: the Microsoft documentation states PBIR is the default; recent Power BI Desktop releases convert a legacy report to PBIR when it is saved. Check the current PBIR documentation before relying on the legacy format.
- **Power BI Premium P SKUs** are being retired at the end of each customer's agreement term, with Fabric F SKUs as the replacement: the move is a workspace reassignment, not automatic. Follow the Microsoft Premium-to-Fabric migration guide; validate refreshes, gateways and pipelines per workspace.
- **Legacy Q&A** natural-language feature: deprecation announced (see `powerbi-ai-readiness` for the replacement and how to prepare the model). Check the current date in the Microsoft documentation.
- **Azure Analysis Services**: Microsoft provides an AAS-to-Power BI migration feature and guidance; see [references/mapping-excel-ssrs.md](references/mapping-excel-ssrs.md).

## Process

1. **Archive** the source and record where in `MIGRATION.md` (location by function, no personal path).
2. **Inventory** with [references/inventory-template.md](references/inventory-template.md); ask for usage data (activity log, server logs, view counts) instead of guessing.
3. **Present** the keep / merge / retire proposal and **wait for the owner's decision**.
4. Map, rebuild, prove parity per model; report progress as a table asset / mapping / parity / cut-over state.
5. Plan cut-over and retirement with [references/parity-and-cutover.md](references/parity-and-cutover.md); start the takeover process of `powerbi-project` once the project is in PBIP.

## References

- [references/inventory-template.md](references/inventory-template.md) — `MIGRATION.md` template.
- [references/pbix-to-pbip.md](references/pbix-to-pbip.md) — format conversions and thin-report split.
- [references/mapping-tableau.md](references/mapping-tableau.md) — Tableau → Power BI concepts.
- [references/mapping-qlik.md](references/mapping-qlik.md) — Qlik → Power BI concepts.
- [references/mapping-excel-ssrs.md](references/mapping-excel-ssrs.md) — Excel / Power Pivot, SSRS, Looker, SSAS / AAS.
- [references/parity-and-cutover.md](references/parity-and-cutover.md) — parity test plan, parallel run, communication, rollback, retirement.
