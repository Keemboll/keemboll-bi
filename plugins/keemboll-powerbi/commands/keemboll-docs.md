---
description: User guide of the keemboll-powerbi plugin (skills, subagents, lean.py script, project files, working method, other agents). Optional argument: a section.
argument-hint: "[installation | skills | examples | project | agents | lean | debt | method | security | troubleshooting]"
---

Show the user the guide below, **without running or changing anything**. Answer in the user's language.

- If `$ARGUMENTS` is empty: show the "Overview" section, then the table of contents and how to open a section (`/keemboll-docs <section>`).
- If `$ARGUMENTS` matches a section (or is close to one): show only that section, in full.
- If `$ARGUMENTS` is a question ("how do I audit a model?"): answer from this guide and name the section concerned.
- Always end with a line "Installed version:" followed by the result of `claude plugin list` for `keemboll-powerbi` if you can read it; otherwise omit that line.

---

# keemboll-powerbi — user guide

## Overview

`keemboll-powerbi` gives a coding agent the **methods and working rules** to run and build a BI project with Power BI and Microsoft Fabric, from scoping to operations. It complements the Microsoft skills (`fabric-skills`, `powerbi-authoring`), which handle the **mechanics** (PBIP files, Fabric APIs, connection to Power BI Desktop). Skills load **automatically** from your request: just write what you want.

Every skill ships sensible defaults (naming, formats, thresholds, design tokens). If your team has its own rules, write them in a `TEAM_RULES.md` at the project root: the agent reads it first and it wins over every default (see `powerbi-conventions`).

| Section | Content |
|---|---|
| `installation` | Prerequisites and installation |
| `skills` | The 20 skills and when they load |
| `examples` | Ready-to-use requests |
| `project` | Phases of a BI project and files at the project root |
| `agents` | Subagents shipped; use with Codex, Grok, Gemini... |
| `lean` | The `lean.py` analysis script |
| `debt` | `DEBT.md` and `CHANGES.md` |
| `method` | The recommended way of working |
| `security` | Sensitive data and guardrails |
| `troubleshooting` | Common problems |

## installation

Prerequisites on the workstation: **Git**, **Python 3.8+** (for `lean.py`), **Claude Code**. For the Microsoft skills and their modeling MCP server: **Azure CLI** (`az login --allow-no-subscriptions`) and **Node.js LTS**.

```powershell
# Microsoft skills (PBIP / Fabric mechanics) — optional but recommended
claude plugin marketplace add microsoft/skills-for-fabric
claude plugin install fabric-skills@fabric-collection
claude plugin install powerbi-authoring@fabric-collection

# This plugin
claude plugin marketplace add keemboll/keemboll-bi
claude plugin install keemboll-powerbi@keemboll-bi
```

Then in Claude Code: `/plugin` → **Marketplaces** → `keemboll-bi` and `fabric-collection` → **Enable auto-update**. Check with `/mcp` that the Microsoft modeling MCP server is connected (otherwise **Reconnect**).

Reports must be saved in **PBIP** format (Power BI Desktop → File → Save as → *Power BI project*). A `.pbix` file: see `powerbi-migration`.

## skills

**Run and deliver**

| Skill | Loads when you... |
|---|---|
| `powerbi-project` | start or take over a project, scope a need, define KPIs, ask for the next step or whether a deliverable is done |
| `powerbi-migration` | move a PBIX to PBIP, or reports from Tableau, Qlik, Excel / Power Pivot, SSRS or another tool to Power BI |
| `powerbi-governance` | design or review RLS / OLS roles, decide who sees what, prepare a publication (sensitivity, endorsement, access) |
| `powerbi-testing` | want to check a model or a measure, prove a change broke nothing, test security, run an acceptance session |
| `powerbi-alm` | organize the repository, branches, environments, a release, continuous integration or a fabric-cicd deployment |
| `powerbi-documentation` | document a model or a report: data dictionary, report sheet, release notes, handover |
| `powerbi-operations` | a refresh failed, data is stale, users report wrong numbers, or for a health review, a runbook, retiring unused reports |

**Build the model**

| Skill | Loads when you... |
|---|---|
| `powerbi-conventions` | change a model or a report; audit "against our conventions" (naming, descriptions, formats, approval process, existing model, confidentiality, `TEAM_RULES.md`) |
| `powerbi-data-modeling` | design or rework a model: star schema, grain, SCD, role-playing dimensions, date table |
| `powerbi-power-query` | write or review M code: staging, parameters, query folding, incremental refresh |
| `powerbi-direct-lake` | choose a storage mode, or design a model on OneLake Delta tables (framing, fallback, guardrails) |
| `powerbi-tmdl` | read or change the `.tmdl` files of a PBIP project |
| `powerbi-dax-library` | write measures: YTD, PY, ratios, rankings, new customers, Plan / PY toggles, calendar-based time intelligence, visual calculations |
| `powerbi-dax-udf` | package repeated DAX logic in user-defined functions (`functions.tmdl`) |
| `powerbi-performance` | a page or a measure is slow; you want to optimize DAX, model or Power Query |
| `powerbi-ai-readiness` | prepare a model for Copilot or Fabric data agents: descriptions, AI data schema, verified answers, AI instructions, AI test set |

**Build the report**

| Skill | Loads when you... |
|---|---|
| `powerbi-mockup` | want an HTML mockup of a page from the real model, before building |
| `powerbi-report-design` | design or review a page: four questions, grid, colours, SVG backgrounds, accessibility |
| `powerbi-html-visuals` | want an SVG / HTML visual in DAX (sparkline, progress bar, KPI card) |
| `powerbi-lean` | ask for a review, an audit, where a field is used, the state of the debt or the change log |

## examples

| Goal | Request to write |
|---|---|
| Discover a model | "List the tables, measures and relationships of the model in this project." |
| Audit | "Audit the model against our conventions." / "Run a powerbi-lean audit." |
| Before a rename | "Where is the measure [Measure name] used?" |
| Safe fixes | "Apply the audit fixes that have no visual impact (date table, summarizeBy, hiding). Show me the plan first." |
| New measure | "Add a year-to-date and a change vs PY measure for [Measure]. Show me the DAX first." |
| Fiscal or retail calendar | "Set up calendar-based time intelligence for our 4-4-5 retail calendar." |
| Repeated logic | "These five measures repeat the same YoY logic: propose a user-defined function." |
| Power Query | "Review the M of Fact_Sales: does it fold? Set up incremental refresh." |
| Storage mode | "Our data is in a Fabric lakehouse: Import or Direct Lake? Explain the trade-offs." |
| New page | "Make an HTML mockup of a [subject] monitoring page from the model." |
| Slowness | "This visual takes 30 s to load: diagnose with powerbi-performance, change nothing." |
| Before commit | "Do a powerbi-lean review of my changes." |
| Debt | "Where does the project's debt stand?" / "Close D-004: the fix is done and checked." |
| Start a project | "Scope a new [subject] monitoring report: ask me the scoping brief questions." |
| KPI | "Add the indicator [name] to KPI.md; here is the business definition." |
| Where are we? | "Where does this project stand and what is the next step?" |
| Migration | "Migrate this Tableau workbook to Power BI: start with the inventory." / "Convert this PBIX to a PBIP project." |
| Security | "Design RLS roles by region, show me the plan and the test protocol before writing." |
| Tests | "Write the model check queries (keys, integrity, reconciliation) in tests/." |
| Non-regression | "I am about to change [Measure]: prepare the before / after test." |
| Copilot | "Is this model ready for Copilot? Write AI_INSTRUCTIONS.md and an AI question set." |
| Release | "Go through the release checklist and tell me what blocks." |
| CI / deployment | "Set up CI that runs lean.py on every pull request." / "Deploy with fabric-cicd from dev to test." |
| Documentation | "Generate DATA_DICTIONARY.md and list the measures without a description." |
| Refresh failure | "Last night's refresh failed with this error: triage it." |
| Health review | "Run the quarterly health review and update RUNBOOK.md." |
| Independent opinion | "Have powerbi-auditor audit this project while I keep working." |

## project

The `powerbi-project` skill splits a project into phases; each has a deliverable, an authoritative skill and an exit criterion:

**scoping → modeling → measures → mockup → report → testing and acceptance → release → operations**

Files at the project root (next to the `.pbip`), versioned with it:

| File | Role | Skill |
|---|---|---|
| `TEAM_RULES.md` | Optional: the team's own rules, overriding skill defaults | `powerbi-conventions` |
| `SCOPE.md` | Audience, business questions, scope, sources, security, success criteria | `powerbi-project` |
| `KPI.md` | KPI catalog (`K-001`...): business definition, formula, measure, owner | `powerbi-project` |
| `MIGRATION.md` | Inventory, keep / merge / retire decisions, mapping and parity status | `powerbi-migration` |
| `SECURITY_MODEL.md` | Who sees what: role × scope matrix, approval, test date | `powerbi-governance` |
| `tests/` and `tests/ACCEPTANCE.md` | DAX check queries (`T-001`...) and acceptance record | `powerbi-testing` |
| `AI_INSTRUCTIONS.md`, `tests/AI_QUESTIONS.md` | AI instructions and the question set that proves AI answer quality | `powerbi-ai-readiness` |
| `DATA_DICTIONARY.md`, `REPORT.md`, `RELEASE_NOTES.md` | Data dictionary generated from the model, report sheet, release notes | `powerbi-documentation` |
| `DEBT.md`, `CHANGES.md` | What remains to fix, what has been done | `powerbi-lean` |
| `RUNBOOK.md`, `incidents/` | How the published content is run; post-incident notes (`I-001`...) | `powerbi-operations` |

None of these files contains real values or people's names. Business decisions (KPI definition, threshold, scope) stay with the user: the agent proposes, it does not decide.

## agents

**Subagents shipped** (the agent delegates to them when the task fits, or on request: "have powerbi-auditor audit this"):

| Subagent | Role |
|---|---|
| `powerbi-analyst` | Scoping: `SCOPE.md`, `KPI.md`, progress report; read-only on the model |
| `powerbi-modeler` | Semantic model, Power Query, DAX measures and functions, once the plan is approved |
| `powerbi-report-designer` | Mockup, layout and visuals of a report page |
| `powerbi-tester` | Check queries, non-regression, RLS tests, migration parity, `ACCEPTANCE.md` |
| `powerbi-ai-curator` | Readiness for Copilot and data agents, AI question set |
| `powerbi-ops` | Refresh triage, incidents, health review, `RUNBOOK.md`; read-only on production |
| `powerbi-auditor` | **Read-only** reviewer: audit, review of a change, check before release |

**Other agents** (Codex, Grok, Gemini, GitHub Copilot, Cursor...): the skills use the open Agent Skills format and install into a project with `python scripts/install.py --agent <agent> --target <project>` from a copy of the `keemboll/keemboll-bi` repository. Details and folders per agent: `docs/agents.md` in that repository. The whole team then applies the same rules, whatever the tool.

## lean

**Read-only** Python script shipped with `powerbi-lean`. The agent runs it itself; you can run it too:

```powershell
python "<skill folder>/scripts/lean.py" audit <project>                 # full audit
python "<skill folder>/scripts/lean.py" audit <project> --changed       # files changed since the last commit
python "<skill folder>/scripts/lean.py" usage <project>                 # fields used per page / visual
python "<skill folder>/scripts/lean.py" usage <project> --field "[Measure]"
python "<skill folder>/scripts/lean.py" debt <project>                  # state of DEBT.md + CHANGES.md
python "<skill folder>/scripts/lean.py" catalog <project>               # data dictionary (Markdown) on standard output
```

`--json` gives machine-readable output. "Unused" = not used by **this** report: check the lineage view of the workspace before deleting.

## debt

Two files at the root of each project, versioned with it:

- `DEBT.md`: what remains to fix (`D-001`...), with priority and due date.
- `CHANGES.md`: what has been fixed or added (`C-001`...), newest first; it fills up as the debt goes down.

Closing a debt: `C-xxx` entry in the log → `D-xxx` moved to "Closed" with `**Change**: C-xxx` → `lean.py debt` without inconsistency → one commit `C-xxx: ...`. Partial progress: `D-xxx (partial)`. Existing project without a log: "Initialise CHANGES.md from the Git history".

## method

0. **Scoping** (`SCOPE.md`, `KPI.md`) for a new project or report; **migration inventory** if the starting point is not a PBIP project.
1. Read-only **audit**.
2. Prioritized **plan**: first what does not change visuals, renames last.
3. **Backup commit**; Power BI Desktop saved.
4. **HTML mockup** for any new page.
5. Step-by-step **execution**; DAX and M shown before being applied; business decisions left to the user.
6. **Verification** in Desktop (before / after values) and human review.
7. **Tests and acceptance** (`tests/`, `tests/ACCEPTANCE.md`); security checked per role; AI question set if the model is exposed to AI.
8. **powerbi-lean review**, log, regenerated documentation, commit; the release follows the `powerbi-alm` checklist.
9. **Operations**: `RUNBOOK.md`, refresh and capacity watch, quarterly health review.

## security

- The agent reads the project's **metadata** (names, DAX, M): check that this is allowed for the project.
- **Data** (`.pbi/cache.abf`) must never be read or committed: `.gitignore` + a `deny Read(**/.pbi/cache.abf)` rule in `~/.claude/settings.json`.
- DAX queries through the MCP server return real data: approve them one by one (`ask` rule).
- Mockups use fictitious values only; `DEBT.md`, `CHANGES.md`, `RUNBOOK.md` and incident notes never contain real values.
- Descriptions and AI instructions are readable by everyone with access to the model: no secrets or personal data.
- Private repositories only; no automatic `git push`, no deployment without an explicit request.

## troubleshooting

| Symptom | Fix |
|---|---|
| Skills missing | `claude plugin list`; `claude plugin update keemboll-powerbi@keemboll-bi`; restart `claude` |
| Modeling MCP server shown as × | `/mcp` → Reconnect; if frequent: `$env:MCP_TIMEOUT="60000"` before `claude` |
| Write refused by auto mode | Project under Git + `.claude/settings.local.json`, or default mode (Shift+Tab) |
| `python` opens the Microsoft Store | `winget install Python.Python.3.12`, then reopen the terminal |
| Changes not visible in Desktop | Apply external changes (preview option of recent Desktop versions) or reopen the `.pbip` — see `powerbi-tmdl` |
| Very slow visual | "Diagnose with powerbi-performance"; copy the query from Performance analyzer into DAX Studio |
| Refresh failed | "Triage this refresh failure" — `powerbi-operations` |

Contributing (new rule, new visual reference): see the `README.md` of the `keemboll/keemboll-bi` repository.
