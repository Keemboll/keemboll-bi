# `tests/ACCEPTANCE.md` template

Copy the block below into `tests/ACCEPTANCE.md`. **No real sensitive value**: the "Result" column contains *pass*, *fail* or *not run*; figures stay outside the repository. People are referred to by their **function**.

```markdown
# Acceptance — <project name>

Version tested: <branch or commit> — Environment: <development / test>
Data period: <e.g. up to end of 2026-10>

## Summary

| Level | Cases | Pass | Fail | Not run |
|---|---|---|---|---|
| 1 Integrity | 4 | 4 | 0 | 0 |
| 2 Reconciliation | 2 | 2 | 0 | 0 |
| 3 Measures | 6 | 5 | 1 | 0 |
| 4 Regression | 1 | 1 | 0 | 0 |
| 5 RLS | 4 | 4 | 0 | 0 |
| 6 Report | 5 | 5 | 0 | 0 |

## Cases

| Test | Level | Case | Expected | Result | Run by | Date | Note |
|---|---|---|---|---|---|---|---|
| T-001 | 1 | Unique customer keys | Zero rows | pass | user (DAX Studio) | YYYY-MM-DD | |
| T-010 | 2 | Monthly net sales = source system | Equal within 0.01 per month | pass | user | YYYY-MM-DD | Source: accounting extract |
| T-020 | 3 | Net Sales PY on the first year | Blank, no error | fail | agent (with agreement) | YYYY-MM-DD | Returns 0 → D-007 |
| T-050 | 5 | RLS_Region, single-region profile | Only one region visible | pass | user (View as) | YYYY-MM-DD | |
| T-051 | 5 | User outside the security table | No rows | pass | user | YYYY-MM-DD | |

## Gaps

| Test | Gap observed (no value) | Cause | Follow-up |
|---|---|---|---|
| T-020 | Zero instead of blank | Unneeded `COALESCE` | Fixed — C-012 / or debt D-007, due YYYY-MM-DD |

## Decision

| Item | Value |
|---|---|
| Business acceptance led by (function) | <e.g. Head of financial control> |
| Date | YYYY-MM-DD |
| Decision | <accepted / accepted with reservations / rejected> |
| Reservations | <D-xxx, D-yyy — or none> |
| Release to production authorized | <yes / no> |
```

Upkeep rules:

- One acceptance per version released to production: keep the previous ones in the Git history rather than stacking tables.
- *Not run* is an honest result; by default, it blocks the "accepted" decision for levels 1, 2 and 5.
- The `D-xxx` and `C-xxx` identifiers are those of `DEBT.md` and `CHANGES.md` (`powerbi-lean`).
- The dates of RLS tests are carried over to `SECURITY_MODEL.md` (`powerbi-governance`).
