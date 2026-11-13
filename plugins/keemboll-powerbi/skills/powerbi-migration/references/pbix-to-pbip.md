# Format migrations inside Power BI

## Why

A `.pbix` is a binary package: it cannot be diffed or reviewed. A Power BI project (PBIP) stores the semantic model in **TMDL** (one file per table, role, culture...) and the report in **PBIR** (one file per page, per visual, per bookmark), which makes diffs, review and parallel work possible (`powerbi-alm`). Microsoft documentation: [Power BI Desktop projects](https://learn.microsoft.com/power-bi/developer/projects/projects-overview), [semantic model folder](https://learn.microsoft.com/power-bi/developer/projects/projects-dataset), [report folder and PBIR](https://learn.microsoft.com/power-bi/developer/projects/projects-report).

## PBIX → PBIP

1. **Archive the original `.pbix`** outside the repository (rule 1 of the skill). Never commit the `.pbix`: it contains the data.
2. In Power BI Desktop: **File → Save as**, type *Power BI project files (*.pbip)*. Conversion is done in Desktop only; Microsoft documents no programmatic PBIX → PBIP conversion. Use a short root folder: long object names can exceed the Windows path length limit.
3. Check the storage formats Desktop used (preview options and defaults change between releases — check the current documentation):
   - model: a `definition\` folder (TMDL) rather than `model.bim` (TMSL);
   - report: a `definition\` folder (PBIR) rather than `report.json` (PBIR-Legacy).
4. **Check `.gitignore` before the first commit** (`powerbi-alm`): `.pbi/cache.abf` holds the loaded data and `.pbi/localSettings.json` is per user; both must be ignored. Desktop creates a `.gitignore` only when none exists in the folder or parent repository — an existing one may lack these lines.
5. `git status`: no `cache.abf`, no `.pbix`, no file with data. Then look for **data values persisted in report metadata**: PBIR can store filter values, slicer selections and series-specific formatting in `visual.json` and bookmarks (Microsoft documents this). Review them before pushing anywhere shared.
6. **First commit = the unmodified conversion** (`chore: convert <Name> to PBIP`). No cleaning, no renaming in that commit: every later change must show in the diff.
7. Run `lean.py audit` (`powerbi-lean`), then follow *Taking over an existing project* in `powerbi-project`.

## `model.bim` (TMSL) → TMDL

- A project saved in TMSL has a `model.bim` file; in TMDL it has a `definition\` folder. Re-saving the project in Desktop with the TMDL format option switches it; the option name and default depend on the Desktop release — check the semantic model folder documentation.
- Commit the TMSL version first, then the TMDL conversion alone in its own commit: the diff is large but mechanical, and nobody reviews it line by line. Check after conversion that the model opens, refreshes and that measures return the same values (`powerbi-testing`, level 4 non-regression).
- TMDL syntax and editing rules: `powerbi-tmdl`.

## Legacy report (`report.json`) → PBIR

- Microsoft documents PBIR as generally available and the default report format, and states that editing and saving a PBIR-Legacy report converts it to PBIR, with a temporary backup kept by Desktop and by the service. Retention periods and the exact releases concerned are in the PBIR documentation; check it rather than relying on a figure here.
- Commit the legacy version before converting, so that Git — not a temporary backup — is the rollback.
- Existing pages and visuals keep their generated names after conversion; renaming PBIR folders is allowed but can break references (drillthrough, bookmarks). Do not rename during the migration commit.

## Thin-report split (many PBIX → one shared model + thin reports)

Situation: several PBIX files each carry a copy of the same model, with drifting measures.

1. **Inventory** the copies in `MIGRATION.md`: tables, measures and their differences (same name, different formula is the dangerous case).
2. **Choose the reference model** with the owner; reconcile diverging measures in `KPI.md` (one definition per KPI, `powerbi-project`).
3. Build the **shared model** project (TMDL), publish it per `powerbi-alm`.
4. For each report: a report-only project whose `definition.pbir` points to the published model (`byConnection`) or, in the same repository, to the model folder (`byPath`). Connection strings and identifiers stay **out of the repository** where the team's rules require it (`powerbi-alm`).
5. **Rename impact**: a report connected to a shared model breaks silently when a measure or column it uses is renamed or removed. Before any rename in the shared model, run `lean.py usage --field` on **every** connected report (`powerbi-lean`) and list the impacts in the PR.
6. Report-level measures created in thin reports are invisible to other reports: move the reusable ones into the shared model.
7. Prove parity per report (non-regression against the old PBIX), then retire the old PBIX files.
