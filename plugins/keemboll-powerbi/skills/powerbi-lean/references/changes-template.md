# CHANGES.md template

Change log of the project, at the root (next to the `.pbip` and `DEBT.md`), versioned with the project. **Newest first.** It fills up as the debt goes down: every closed debt has its entry; changes that are not debt-related (new page, new measure) are recorded too.

```markdown
# Change log — <project name>

## C-002 · 2026-10-20 · Duplicate measures merged
- **Debt**: D-002
- **Type**: refactoring
- **Changed objects**: `_Measures[Net Sales LY]` rewritten to reference `[Net Sales PY]`
- **Before → after**: two identical DAX expressions → one base measure + one reference
- **Report impact**: no visual changed (checked with `lean.py usage`)
- **Verification**: values compared before/after over 3 periods and 2 regions: identical
- **Commit**: message `C-002: …` · **By**: <name>

## C-001 · 2026-10-15 · Date table marked
- **Debt**: D-001
- **Type**: fix
- **Changed objects**: `Dim_Date` (dataCategory: Time, isKey on Date)
- **Before → after**: table not marked → official date table
- **Report impact**: `[Net Sales YTD]` re-checked
- **Verification**: monthly totals identical; year-to-date values identical
- **Commit**: message `C-001: …` · **By**: <name>
```

## Rules

- Identifiers **C-001, C-002…** are never reused. `python lean.py debt <project>` gives the next one.
- **Debt**: one or more `D-xxx`, or `none` for a change that is not debt-related. `D-xxx (partial)` (or `(in progress)`) for progress that does not close the debt yet: it then stays under "Open". A debt cited here without that marker must be moved to "Closed" in `DEBT.md` with `**Change**: C-xxx`.
- **Type**: fix · refactoring · cleanup · performance · new feature · documentation.
- **Verification**: describe what was compared and the verdict (identical / difference explained). **Never copy real values** (KPI figures, names of people or organisations).
- **Commit**: the commit message starts with the identifier (`C-002: merge duplicate measures`); `git log --grep "C-002"` finds the commit without having to copy its hash.
- One change = one commit that contains the model/report change **and** the updates of `DEBT.md` and `CHANGES.md`.

## Initialise the change log on a project that already has debt

1. **Invent nothing**: rebuild only from `git log` / `git show` (since `DEBT.md` was created) and from what `DEBT.md` already mentions as done.
2. File header: *"Log started on yyyy-mm-dd; earlier entries are rebuilt from the Git history."*
3. One `C-xxx` entry per past change, **numbered in chronological order** (C-001 = the oldest) but **listed from newest to oldest**. For these entries:
   - **Commit**: the real short hash (`abc1234`), since the commit exists;
   - **Verification**: what is known, otherwise "not verified after the fact" — do not claim a verification that did not take place.
4. Debt **fully** fixed in the past → move it to "Closed" in `DEBT.md` (`**Closed on**` = commit date, `**Change**: C-xxx`). Debt **partly** handled → leave it open and cite `D-xxx (partial)`.
5. Changes made before `DEBT.md` was created (initial commit, putting the project under Git): a single `none` entry of type "documentation" is enough.
6. Finish with `python lean.py debt <project>`: zero inconsistency expected.
7. Single commit: initialising the log is not a change to the model, so it gets no `C-xxx` identifier; use the message `docs: initialise CHANGES.md (history backfill)`.
