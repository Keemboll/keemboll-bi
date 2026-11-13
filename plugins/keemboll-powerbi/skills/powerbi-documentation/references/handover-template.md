# HANDOVER.md template

A short file for the person taking over the project. It **points** to the other files instead of copying them; it only contains what is written nowhere else.

```markdown
# Handover — <project name> · <date>

## In one sentence
<What this project is for, and for whom.>

## Where to find what

| Topic | File |
|---|---|
| Requirements, scope, KPIs | `SCOPE.md`, `KPI.md` |
| Model: tables, measures, relationships | `DATA_DICTIONARY.md` (regenerated on <date>) |
| Report: pages and audience | `REPORT.md` |
| Security and access | `SECURITY_MODEL.md` |
| Tests and acceptance | `tests/`, `tests/ACCEPTANCE.md` |
| What remains to be fixed | `DEBT.md` |
| What has been done | `CHANGES.md`, `RELEASE_NOTES.md` |

## Sources and refresh
- Sources: <systems, without connection string or identifier>
- Refresh: <frequency, who is alerted on failure>
- Environments and deployment: see `powerbi-alm` — <workspaces named by their role: dev / test / prod>

## What to know before touching the model
- <non-obvious modelling choice and its reason>
- <sensitive measure: definition agreed with the business, do not change it without them>
- <known pitfall: object used by another report, risky rename>

## In progress and next steps
- <work started, branch, state>
- <priority debts>

## Contacts
- Business owner: <job title> · Technical lead: <job title> · Access: <whom to ask>
```

## Rules

- Regenerate `DATA_DICTIONARY.md` and run `lean.py debt` **before** writing the handover: it cites their state as of today.
- The "What to know" section is filled in with the user: these are the decisions and pitfalls that neither the model nor Git tell. Do not fill it in by deduction.
- Job titles rather than person names; no tenant or workspace identifier, no secret, no real value.
- An empty section is deleted or says "nothing to report": no padding.
