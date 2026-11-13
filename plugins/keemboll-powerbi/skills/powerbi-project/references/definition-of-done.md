# Definition of done per deliverable

A deliverable is **done** when all its checks are true. This page says **what to check and where the rule lives**; it does not copy the rules. An unmet but accepted check = a `D-xxx` entry in `DEBT.md` (`powerbi-lean`), never a silent omission.

## Migration — only when the starting point is not a PBIP project

| Check | Rule in |
|---|---|
| Project saved as PBIP and reopening without error; what was not migrated is listed | `powerbi-migration` |
| Numbers reconciled with the legacy report before it is retired | `powerbi-migration`, `powerbi-testing` |

## Scoping — `SCOPE.md`, `KPI.md`

| Check | Rule in |
|---|---|
| Audience, decisions and 3 to 7 business questions filled in | `powerbi-project` (scoping brief) |
| Every question has at least one KPI, every KPI has a question | `powerbi-project` (KPI catalog) |
| No blocking `TO CONFIRM`; open points dated and assigned | `powerbi-project` |
| Scope and KPIs **approved** by the requester (date and role) | `powerbi-project` |

## Semantic model — `*.SemanticModel`

| Check | Rule in |
|---|---|
| Star schema, grain of each fact documented, date table marked | `powerbi-data-modeling` |
| Naming, hiding, `summarizeBy`, descriptions, formats | `powerbi-conventions` |
| Valid TMDL, project reopens without error in Desktop | `powerbi-tmdl` |
| Storage mode chosen and justified; cardinalities under control | `powerbi-data-modeling`, `powerbi-performance` |
| Queries: folding checked, environment-specific values in parameters, incremental refresh where the volume calls for it | `powerbi-power-query` |
| Data in OneLake: Direct Lake storage design checked | `powerbi-direct-lake` |

## Measures

| Check | Rule in |
|---|---|
| Every `approved` KPI has its measure; status moved to `implemented` | `powerbi-project` (KPI catalog) |
| Standard patterns reused rather than rewritten | `powerbi-dax-library` |
| DAX user-defined functions, when the project uses them, follow the skill | `powerbi-dax-udf` |
| Description, `WHAT` / `HOW` / `NOTE` comment, display folder, format | `powerbi-conventions` |
| No known DAX anti-pattern | `powerbi-performance` |
| Value checked by a test | `powerbi-testing` |

## Mockup

| Check | Rule in |
|---|---|
| Built from the real model; each element labeled with its field | `powerbi-mockup` |
| Missing measures listed, then created or removed from the page | `powerbi-mockup` |
| Approved by the requester before any build | `powerbi-project` |

## Report — `*.Report`

| Check | Rule in |
|---|---|
| Each page answers the four questions; grid, theme, titles | `powerbi-report-design` |
| Accessibility (contrast, alt text, tab order) | `powerbi-report-design` |
| HTML / SVG visuals compliant and readable | `powerbi-html-visuals` |
| Page load times acceptable | `powerbi-performance` |

## Tests and acceptance — `tests/`, `tests/ACCEPTANCE.md`

| Check | Rule in |
|---|---|
| Measure tests and reconciliation with the source passing | `powerbi-testing` |
| Security tested per role | `powerbi-testing`, `powerbi-governance` |
| Acceptance signed by the business | `powerbi-testing` |

## Release

| Check | Rule in |
|---|---|
| `powerbi-lean` review: verdict *ready to commit* | `powerbi-lean` |
| `SECURITY_MODEL.md` up to date: roles, access, sensitivity | `powerbi-governance` |
| `DATA_DICTIONARY.md` and release notes up to date | `powerbi-documentation` |
| Branch merged, deployment through the planned environment, rollback possible | `powerbi-alm` |
| `CHANGES.md` completed (`C-xxx` entries); remaining debt recorded (`D-xxx`) | `powerbi-lean` |
| `RUNBOOK.md` written before go-live | `powerbi-operations` |
| **Only if the model is exposed to Copilot or data agents**: AI readiness checked, `AI_INSTRUCTIONS.md` up to date | `powerbi-ai-readiness` |

## Operations

| Check (recurring) | Rule in |
|---|---|
| Refreshes monitored; they succeed and meet the delay agreed at scoping | `powerbi-operations` |
| Incidents handled and recorded; `RUNBOOK.md` kept up to date | `powerbi-operations` |
| Capacity and usage reviewed; unused content identified | `powerbi-operations`, `powerbi-lean` |
| Slow pages or refreshes diagnosed | `powerbi-performance` |
| Debt reviewed; overdue items handled or rescheduled | `powerbi-lean` |
| Any change that adds a business question goes back through scoping → KPI → mockup | `powerbi-project` |
