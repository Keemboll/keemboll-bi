---
name: powerbi-lean
description: "Lean Power BI models and reports, and review of changes: fewer objects, not less documentation. Three modes: review (review the git diff of a PBIP project), audit (unused measures and columns, duplicate DAX, hardcoded values, FILTER over a whole table, summarizeBy, visible keys, date table) and debt (DEBT.md register of accepted shortcuts and CHANGES.md change log that fills up as the debt goes down). Ships a read-only Python script (lean.py) that also lists the fields used by the report before a rename. Use after changing a model or report, when taking over a project, before a refactoring or a publication, or to record and close technical debt. Triggers: review, audit, change log, changelog, close a debt, debt progress, cleanup, simplify, unused, duplicate, technical debt, tech debt, refactor, before rename, where is this measure used, impact."
---

# powerbi-lean — fewer objects, not less documentation

Goal: every measure, column or table must **serve a question** of the report. Remove what is superfluous (duplicates, dead objects, hardcoded values, copied logic); **never remove** descriptions, `// WHAT:` / `// HOW:` / `// NOTE:` comments, display folders or formats.

Apply `powerbi-conventions` (validation, Git, existing model, confidentiality), `powerbi-performance` (DAX rewrites) and `powerbi-dax-library` (replacement patterns). **Read-only by default**: no change without a validated plan.

## The script

`scripts/lean.py` (in this skill's folder, Python 3.8+, standard library only) analyses a PBIP project **without modifying anything**: TMDL of the model + PBIR of the report.

```bash
python "<skill folder>/scripts/lean.py" audit "<PBIP project folder>"                 # full audit
python "<skill folder>/scripts/lean.py" audit "<folder>" --changed                    # files changed since the last commit
python "<skill folder>/scripts/lean.py" usage "<folder>"                              # fields used per page / visual
python "<skill folder>/scripts/lean.py" usage "<folder>" --field "'Table'[Column]"    # where a field is used
python "<skill folder>/scripts/lean.py" usage "<folder>" --field "[Measure]"
python "<skill folder>/scripts/lean.py" debt "<folder>"                               # state of DEBT.md + CHANGES.md
python "<skill folder>/scripts/lean.py" catalog "<folder>"                            # data dictionary (Markdown, see powerbi-documentation)
```

Add `--json` for machine-readable output. On Windows use `python` (or `py`); elsewhere `python3`. The folder can be the one holding the `.pbip`, the `*.SemanticModel` folder, or the `.pbip` file itself. What the script checks and its limits: [references/audit-rules.md](references/audit-rules.md).

Always **run the script** rather than guess where a field is used: it is the authority for "used / unused".

## `review` mode — review a change

When: after a change to the model or the report, before the commit.

1. `git status` and `git diff` in the project folder (TMDL and PBIR).
2. `lean.py audit <folder> --changed`: findings limited to the changed files.
3. Read the diff against the grid in [references/review-grid.md](references/review-grid.md): duplicated logic, a measure that rewrites an existing measure, hardcoded value, documentation removed, rename without updating the visuals, copied `lineageTag`.
4. Return **at most 7 findings**, ranked by impact: object, problem, proposed fix (with DAX when useful). End with a verdict: *ready to commit* / *to fix*.
5. Change nothing without agreement.

## `audit` mode — review the whole project

When: taking over a model, before a redesign, before publication.

1. `lean.py audit <folder>` (+ `usage` when renames are being considered).
2. Complete it with a targeted read of what the script cannot see: near-duplicate logic (same calculations with variations), "catch-all" measures (a SWITCH that copies other measures), misleading names.
3. Report a table **prioritised by gain / risk**:
   - **No visual impact** first: date table, `summarizeBy`, hiding keys, formats, descriptions.
   - **Cleanup**: removal of unused objects (after confirming that no other connected report uses them), merging duplicates.
   - **Refactoring**: copied measures → composition of base measures; hardcoded values → measures or reference tables.
   - **Renames** last, with the `usage` inventory of each object.
4. Offer to record in `DEBT.md` whatever will not be fixed right away.

## `debt` mode — register of shortcuts and change log

Two files at the project root, next to the `.pbip`, versioned with it — **never as comments in the published model**:

| File | Role | Template |
|---|---|---|
| `DEBT.md` | What remains to be fixed (accepted shortcuts, audit findings not handled) | [debt-template.md](references/debt-template.md) |
| `CHANGES.md` | What has been fixed or added, newest first; fills up as the debt goes down | [changes-template.md](references/changes-template.md) |

- **State**: `python "<skill folder>/scripts/lean.py" debt "<project folder>"` → open / closed debts, progress, priorities, overdue items, next identifiers (D-xxx, C-xxx) and inconsistencies between the two files.
- **Add a debt**: new `D-xxx` entry under "Open"; at the end of an `audit`, offer to record the findings not handled there.
- **Close a debt** (after the fix **and** its verification):
  1. add a `C-xxx` entry at the top of `CHANGES.md`: debt(s) closed, type, changed objects, before → after, impact on the report, verification (no real values);
  2. move the `D-xxx` entry from "Open" to "Closed" with `**Closed on**` and `**Change**: C-xxx`;
  3. run `lean.py debt` again: no inconsistency expected;
  4. a single commit for the change and both files, message `C-xxx: <summary>`.
- **Change that is not debt-related** (new page, new measure): `C-xxx` entry with `**Debt**: none`.
- **Partial progress**: `**Debt**: D-xxx (partial)`, the debt stays open.
- **Project that already has debt but no change log**: rebuild `CHANGES.md` from `git log` and `DEBT.md`, without inventing anything — procedure in [changes-template.md](references/changes-template.md#initialise-the-change-log-on-a-project-that-already-has-debt).
- Never close a debt without a change log entry, and never write a change log entry without having verified the values.

## Rules

- Delete or merge only after the `usage` inventory **and** explicit validation.
- "Unused" = not referenced by **this** report: another report connected to the published model may use it. Say so every time.
- A simplification that changes a result is not a simplification: check the values before/after (control DAX query).
- Never a `TODO` / `shortcut` comment in measures: debt goes into `DEBT.md`.
