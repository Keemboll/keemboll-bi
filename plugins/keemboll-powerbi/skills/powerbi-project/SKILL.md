---
name: powerbi-project
description: "Scope and run a Power BI project end to end: phases (scoping, modeling, measures, mockup, report, acceptance, release, operations), the deliverable and exit criterion of each phase, which skill is authoritative at each step, the SCOPE.md brief, the KPI.md catalog, roles and the definition of done. Load it when starting a project or a new report, when taking over or migrating an existing project, to find out where a project stands, what the next step is or which skill to apply, and before delivering. Triggers: BI project, scoping, requirements, kickoff, project management, phases, planning, roadmap, deliverable, KPI, KPI catalog, definition of done, progress, next step, which skill, project takeover, handover, onboarding, BI lifecycle."
---

# powerbi-project — scope and run a BI project

This skill is the **conductor**: it says **what to do, in which order and with which skill**. It contains no technical rule: each phase points to the skill that is authoritative for it. The Microsoft skills, when installed (`semantic-model-authoring`, `powerbi-report-cli`), remain responsible for the **mechanics** (APIs, files, MCP); otherwise Power BI Desktop or the portal, used by the user.

## Rules

1. **No model without scoping, no report without an approved mockup.** A phase starts only when the exit criterion of the previous one is met, or when the gap is recorded in `DEBT.md`.
2. **Business decisions belong to the user**: KPI definition, threshold, target, scope, business rule, audience. The agent **proposes** (with options and consequences), **does not decide**, and records the decision in `SCOPE.md` or `KPI.md`.
3. **A KPI is implemented only once it is `approved`** in `KPI.md`. A measure with no KPI or no business question is a candidate for removal (`powerbi-lean`).
4. **Never put real values** or personal data in `SCOPE.md`, `KPI.md` or any other management file: only definitions, object names and fictitious orders of magnitude.
5. Apply `powerbi-conventions` before any write (approval, Git, existing model, confidentiality, and the project's `TEAM_RULES.md` when there is one).

## The phases

| # | Phase | Goal | Deliverable | Authoritative skill | Exit criterion |
|---|---|---|---|---|---|
| 1 | Scoping | Know who the report serves and which decisions it informs | `SCOPE.md`, `KPI.md` | `powerbi-project` | Business questions and KPIs **approved** by the requester |
| 2 | Modeling | Star schema at the right grain, loaded by clean queries | `*.SemanticModel` (TMDL) | `powerbi-data-modeling`, `powerbi-power-query`, `powerbi-tmdl`, `powerbi-conventions`; `powerbi-direct-lake` when the data is in OneLake | Every KPI is computable; relationships and date table checked |
| 3 | Measures | One measure per approved KPI | Described, organized measures | `powerbi-dax-library`, `powerbi-dax-udf`, `powerbi-performance` | Every approved `K-xxx` has its measure; values checked |
| 4 | Mockup | Validate the page before building it | HTML mockup | `powerbi-mockup`, `powerbi-report-design` | Mockup approved; no missing measure |
| 5 | Report | Build the approved pages | `*.Report` (PBIR) | `powerbi-report-design`, `powerbi-html-visuals` | Pages match the mockup and the style guide |
| 6 | Testing / acceptance | Prove the numbers are right | `tests/`, `tests/ACCEPTANCE.md` | `powerbi-testing` | Acceptance signed by the business |
| 7 | Release | Deliver safely and reversibly | `SECURITY_MODEL.md`, `DATA_DICTIONARY.md`, release notes; `AI_INSTRUCTIONS.md` if exposed to AI | `powerbi-governance`, `powerbi-alm`, `powerbi-documentation`; `powerbi-ai-readiness` (optional gate) | `powerbi-lean` *ready to commit* review; security tested; deployed |
| 8 | Operations | Keep the report accurate, fast and lean | `RUNBOOK.md`; `DEBT.md`, `CHANGES.md` up to date | `powerbi-operations` (authoritative), `powerbi-lean`, `powerbi-performance` | Continuous: refreshes monitored, incidents handled, debt tracked |

**AI gate (phase 7, optional)**: when the model will be exposed to Copilot or to data agents, apply `powerbi-ai-readiness` before release; otherwise skip it and say so. Whether the model is exposed is a decision of the user, recorded in `SCOPE.md`.

Phases 2 to 5 are **iterative**: deliver one complete page (model → measures → mockup → page) before starting the next. The detail of the checks per deliverable is in [references/definition-of-done.md](references/definition-of-done.md).

## Typical project layout

At the root, next to the `.pbip`, versioned with it:

```
<project>/
├── <Name>.pbip
├── <Name>.SemanticModel/     # model (TMDL)
├── <Name>.Report/            # report (PBIR)
├── AGENTS.md                 # instructions for agents (skills to load, guardrails)
├── TEAM_RULES.md             # optional: team rules overriding skill defaults → powerbi-conventions
├── SCOPE.md                  # scoping brief               → powerbi-project
├── KPI.md                    # KPI catalog                 → powerbi-project
├── DATA_DICTIONARY.md        # data dictionary             → powerbi-documentation
├── REPORT.md                 # report sheet                → powerbi-documentation
├── RELEASE_NOTES.md          # release notes               → powerbi-documentation
├── SECURITY_MODEL.md         # roles, access, sensitivity  → powerbi-governance
├── AI_INSTRUCTIONS.md        # optional: model exposed to AI → powerbi-ai-readiness
├── RUNBOOK.md                # refresh, incidents, contacts → powerbi-operations
├── DEBT.md                   # what remains to fix         → powerbi-lean
├── CHANGES.md                # what has been done          → powerbi-lean
└── tests/                    # tests and ACCEPTANCE.md     → powerbi-testing
```

A missing file means a phase not done: say so, do not create it empty "to look tidy". Exceptions: `TEAM_RULES.md` and `AI_INSTRUCTIONS.md` are optional, and `HANDOVER.md` is written only at a handover (`powerbi-documentation`).

## Process

### New project

1. **Interview** the user with the [references/scope-brief.md](references/scope-brief.md) form — in blocks of 3 to 5 questions, not all at once. Write `SCOPE.md`; mark `TO CONFIRM` whatever has no answer, invent nothing.
2. **Derive the KPIs** from the business questions into `KPI.md` ([references/kpi-catalog.md](references/kpi-catalog.md)), status `proposed`. Get each definition approved.
3. **Present the plan**: phases, deliverables, page order, open points. Wait for approval.
4. Run the phases, loading the authoritative skill each time; at the end of each phase, check the exit criterion and update the KPI statuses.

### Taking over an existing project

0. **Starting point is not a PBIP project** (a `.pbix`, a report from another BI tool, a legacy format): apply `powerbi-migration` first, then come back here.
1. **Read-only audit first**: `powerbi-lean` (`audit` mode), changing nothing.
2. **Locate the project** in the phases: which files of the layout exist, which are up to date.
3. **Rebuild** `SCOPE.md` and `KPI.md` from what exists (pages, measures, descriptions): status `implemented` for what is in place, but the definition is **to be confirmed** by the business — an existing measure is not an approved definition.
4. Record the gaps in `DEBT.md` (`powerbi-lean`, `debt` mode) and propose a prioritized plan. The "existing model" rules of `powerbi-conventions` apply (no renaming unless asked).

### Progress report

On request ("where does the project stand?"): a phase / deliverable / state (*done*, *in progress*, *missing*) / next step table, the number of KPIs per status, the state of the debt and of the changes (`lean.py debt`, see `powerbi-lean`: open `D-xxx`, logged `C-xxx`). Do not declare a phase finished without checking its exit criterion.

## Roles

A role = a scope, skills to load and rights. One person (or one agent) can hold several roles, **but not be both author and reviewer of the same change**.

| Role | Phases | Skills to load | Rights | Subagent |
|---|---|---|---|---|
| Scoping analyst | 1 | `powerbi-project` | Writes `SCOPE.md`, `KPI.md`; read-only on the model | `powerbi-analyst` |
| Modeler | 2 | `powerbi-data-modeling`, `powerbi-power-query`, `powerbi-direct-lake`, `powerbi-tmdl`, `powerbi-conventions`, `powerbi-governance` | Writes `*.SemanticModel` | `powerbi-modeler` |
| DAX developer | 3 | `powerbi-dax-library`, `powerbi-dax-udf`, `powerbi-performance`, `powerbi-conventions` | Writes measures | `powerbi-modeler` |
| Report designer | 4, 5 | `powerbi-mockup`, `powerbi-report-design`, `powerbi-html-visuals` | Writes mockups and `*.Report`; read-only on the model | `powerbi-report-designer` |
| Tester | 6 | `powerbi-testing`, `powerbi-governance` | Writes `tests/` and `tests/ACCEPTANCE.md`; read-only on the model and the report | `powerbi-tester` |
| AI curator | 7 (AI gate) | `powerbi-ai-readiness`, `powerbi-conventions` | Scope set by `powerbi-ai-readiness`; no change to business logic | `powerbi-ai-curator` |
| Operations | 8 | `powerbi-operations`, `powerbi-performance`, `powerbi-lean` | Writes `RUNBOOK.md`; read-only on the model and the report | `powerbi-ops` |
| Reviewer / auditor | 6, 7, 8 | `powerbi-lean`, `powerbi-conventions`, `powerbi-performance`, `powerbi-governance`, `powerbi-testing`, `powerbi-alm`, `powerbi-documentation` | **Read-only**; returns findings and a verdict | `powerbi-auditor` |

A migration (`powerbi-migration`) is run by the modeler and the report designer, each within their rights.

If the agent can delegate to subagents and the plugin's subagents are installed, they hold these roles: `powerbi-analyst` (scoping, `SCOPE.md` / `KPI.md`), `powerbi-modeler` (model and measures), `powerbi-report-designer` (mockup and report), `powerbi-tester` (tests and acceptance), `powerbi-ai-curator` (AI readiness), `powerbi-ops` (operations) and `powerbi-auditor` (read-only review). Otherwise, the agent applies the same roles by **loading the listed skills** and respecting the "Rights" column.

## References

- [references/scope-brief.md](references/scope-brief.md) — scoping questions and `SCOPE.md` template.
- [references/kpi-catalog.md](references/kpi-catalog.md) — `KPI.md` template, statuses, definition rules.
- [references/definition-of-done.md](references/definition-of-done.md) — checks per deliverable, with the authoritative skill.
