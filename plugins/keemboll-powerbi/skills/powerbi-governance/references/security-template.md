# `SECURITY_MODEL.md` template

Copy the block below to the project root, next to the `.pbip`. **No person name, no e-mail, no data value**: functions, group names, scopes.

```markdown
# Security — <project name>

Last updated: YYYY-MM-DD

## Sheet

| Item | Value |
|---|---|
| Business owner (function) | <e.g. Sales management> |
| Technical owner (function) | <e.g. BI team> |
| Data classification | <public / internal / confidential / personal / health> |
| Sensitivity label | <label name> |
| Endorsement | <none / Promoted / Certified> — since YYYY-MM-DD |
| Distribution | <app + audiences> |
| Export of underlying data | <allowed / disabled> |
| Build permission | <groups concerned, or none> |

## Workspace roles

| Environment | Admin | Member | Contributor | Viewer |
|---|---|---|---|---|
| Development | <group> | <group> | <group> | — |
| Production | <group> | <group> | — | — |

## Role × scope matrix

| Role | Type | Filtered table | Visible scope | Attached group(s) | Validated by (function) | Tested on | Result |
|---|---|---|---|---|---|---|---|
| RLS_Region | Dynamic RLS | Dim_Store | The user's regions according to the security table | <group> | <function> | YYYY-MM-DD | pass |
| RLS_Management | Static RLS | — | Everything | <group> | <function> | YYYY-MM-DD | pass |

User attached to no role: sees nothing — tested on YYYY-MM-DD.

## Hidden objects (OLS)

| Role | Hidden table / column | Reason | Visuals or measures concerned |
|---|---|---|---|
| — | — | — | — |

## Security table

| Item | Value |
|---|---|
| Table | <e.g. Dim_User> |
| Source | <reference system the rights come from> |
| Responsible for updates (function) | <function> |
| Refresh frequency | <daily / ...> |

## Sensitive data

| Column or table | Nature | Measure taken |
|---|---|---|
| <table[column]> | <personal / health / financial> | <not loaded / pseudonymized / OLS / aggregated> |

## History

| Date | Change | Requested by (function) | Test |
|---|---|---|---|
| YYYY-MM-DD | Creation of RLS_Region | <function> | T-0xx pass |
```

Upkeep rules:

- Update the file **in the same commit** as the role change.
- The "Tested on" column refers to the cases in `tests/ACCEPTANCE.md` (`powerbi-testing`).
- A known and accepted gap (untested role, sensitive data still loaded) also goes into `DEBT.md` (`powerbi-lean`).
