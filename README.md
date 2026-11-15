# keemboll-bi

[![Validate](https://github.com/Keemboll/keemboll-bi/actions/workflows/validate.yml/badge.svg)](https://github.com/Keemboll/keemboll-bi/actions/workflows/validate.yml) [![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE) [![Part of Keemboll](https://img.shields.io/badge/part%20of-Keemboll-informational)](https://github.com/Keemboll)

> `keemboll-bi` is the first project of the [Keemboll](https://github.com/Keemboll) organization, which hosts open-source BI tooling. Shared guidelines live in the [organization contributing guide](https://github.com/Keemboll/.github/blob/main/CONTRIBUTING.md).

Agent skills to **run and build BI projects with Power BI and Microsoft Fabric** with a coding agent: from scoping to operations, with explicit working rules, ready-made templates and a read-only analysis script.

- **For Claude Code**: a marketplace (`keemboll-bi`) with the `keemboll-powerbi` plugin — 20 skills, 7 subagents and a built-in guide (`/keemboll-bi-docs`).
- **For other agents** (Codex, Grok, Gemini, GitHub Copilot, Cursor...): the same skills, in the open *Agent Skills* format, installed into the BI project by a script — see [docs/agents.md](docs/agents.md).

Every skill works out of the box with sensible defaults (naming, formats, thresholds, design tokens). A team that has its own rules writes them in a `TEAM_RULES.md` at the project root: the agent reads it first and it overrides every default.

---

## Contents

The `keemboll-powerbi` plugin covers the whole life of a project:

| Stage | Skill | Role |
|---|---|---|
| **Run** | `powerbi-project` | Phases of a BI project, `SCOPE.md` brief, `KPI.md` catalog, roles, definition of done |
| | `powerbi-migration` | PBIX → PBIP, Tableau / Qlik / Excel / SSRS → Power BI: inventory, mapping, parity, cut-over |
| **Design the model** | `powerbi-conventions` | Naming, model organization, baseline DAX rules, approval process, `TEAM_RULES.md` |
| | `powerbi-data-modeling` | Dimensional modeling: star schema, grain, keys, SCD, role-playing dimensions, bridge tables |
| | `powerbi-power-query` | M code: staging, parameters, query folding, typing, incremental refresh |
| | `powerbi-direct-lake` | Storage mode choice, Direct Lake on OneLake / SQL endpoint, framing, fallback, Delta hygiene |
| | `powerbi-tmdl` | Reading / writing semantic models in TMDL (PBIP projects) |
| **Calculate** | `powerbi-dax-library` | Standard measures: time intelligence (classic and calendar-based), margins, shares, rankings, toggles, visual calculations |
| | `powerbi-dax-udf` | DAX user-defined functions: when, naming, typing, `functions.tmdl`, tests |
| | `powerbi-performance` | DAX and model optimization (cardinality, VertiPaq, diagnostics) |
| **Build the report** | `powerbi-mockup` | HTML mockup of a page from the real model, before building in Power BI |
| | `powerbi-report-design` | Report style guide: theme, layout, accessibility, choice of visuals |
| | `powerbi-html-visuals` | HTML / SVG visuals generated in DAX (cards, sparklines, progress bars) |
| **Secure and open to AI** | `powerbi-governance` | RLS / OLS, sensitivity labels, endorsement, access and sharing, `SECURITY_MODEL.md` |
| | `powerbi-ai-readiness` | Model ready for Copilot and Fabric data agents: AI data schema, verified answers, AI instructions, AI test set |
| **Verify** | `powerbi-testing` | Model integrity, reconciliation, measure tests, non-regression, RLS tests, acceptance (`tests/`) |
| | `powerbi-lean` | Diff review, audit (unused, duplicates, hard-coded values), `DEBT.md` and `CHANGES.md`; `lean.py` script |
| **Deliver** | `powerbi-alm` | PBIP repository, branches, environments, quality gates, CI, fabric-cicd, release and rollback |
| | `powerbi-documentation` | Generated `DATA_DICTIONARY.md`, report sheet, release notes, handover |
| **Run in production** | `powerbi-operations` | Refresh triage, incidents, capacity and usage watch, `RUNBOOK.md`, retiring unused content |

Subagents (Claude Code): `powerbi-analyst` (scoping), `powerbi-modeler` (model and measures), `powerbi-report-designer` (report pages), `powerbi-tester` (tests and acceptance), `powerbi-ai-curator` (AI readiness), `powerbi-ops` (operations), `powerbi-auditor` (read-only review). The same roles are described in `powerbi-project` for other agents.

Built-in guide: in Claude Code, type **`/keemboll-bi-docs`** (or `/keemboll-bi-docs <section>`: installation, skills, examples, project, agents, lean, debt, method, security, troubleshooting).

## Installation

### Claude Code

Prerequisites: Claude Code, Git, Python 3.8+. Recommended: the Microsoft plugins (they need Azure CLI signed in with `az login --allow-no-subscriptions`).

```powershell
# 1. Microsoft plugins (official source) — recommended
claude plugin marketplace add microsoft/skills-for-fabric
claude plugin install fabric-skills@fabric-collection
claude plugin install powerbi-authoring@fabric-collection

# 2. This plugin
claude plugin marketplace add keemboll/keemboll-bi
claude plugin install keemboll-powerbi@keemboll-bi
```

Local test, before pushing to GitHub:

```powershell
claude plugin marketplace add ./keemboll-bi
claude plugin install keemboll-powerbi@keemboll-bi
```

Enable automatic updates: in Claude Code, `/plugin` → **Marketplaces** → `keemboll-bi` → **Enable auto-update** (same for `fabric-collection`).

### Codex, Grok, Gemini, GitHub Copilot, Cursor and others

Prerequisites: Python 3.8+ and a copy of this repository.

```powershell
git clone https://github.com/keemboll/keemboll-bi
cd keemboll-bi
python scripts/install.py --agent codex --target "C:\path\to\my-bi-project"   # or grok, gemini, copilot, cursor, generic
```

The script copies the skills into the folder the agent reads (`.agents/skills/`, `.grok/skills/`...) and adds a skills index block to the project's `AGENTS.md`, without touching the rest of the file. Running it again updates; `--uninstall` removes everything; `--list` shows the supported agents. For an agent without file access, `python scripts/build_dist.py` produces all the skills in a single Markdown file. Details, folders and limits: [docs/agents.md](docs/agents.md).

## Working alongside the Microsoft skills

| Need | Microsoft skill | Our skill (applied on top) |
|---|---|---|
| Change a semantic model | `semantic-model-authoring` | `powerbi-conventions`, `powerbi-data-modeling`, `powerbi-power-query`, `powerbi-tmdl` |
| Write measures and functions | `semantic-model-authoring` | `powerbi-dax-library`, `powerbi-dax-udf`, `powerbi-performance` |
| Direct Lake models on OneLake | `semantic-model-authoring` | `powerbi-direct-lake` |
| Create / change a report | `powerbi-report-cli` | `powerbi-mockup`, `powerbi-report-design`, `powerbi-html-visuals` |
| Security roles, labels, endorsement | `semantic-model-authoring`, `onelake-catalog-cli` | `powerbi-governance` |
| dev → test → prod promotion, Git sync | `deployment-pipelines-authoring-cli`, `git-integration-operations-cli` | `powerbi-alm` |
| Natural-language questions on the data | `fabriciq` | `powerbi-ai-readiness` (prepare the model so that answers are right) |
| Scoping, migration, tests and acceptance, documentation, operations | — | `powerbi-project`, `powerbi-migration`, `powerbi-testing`, `powerbi-documentation`, `powerbi-operations` |
| Review / audit / clean-up of a PBIP project | — | `powerbi-lean` |

The Microsoft skills handle the **mechanics** (Fabric APIs, PBIR / PBIP files, MCP); ours set the **working rules**. In case of conflict, our conventions win on style choices, never on the technical constraints of the APIs. Without the Microsoft skills (another agent, a workstation without Azure CLI), our skills still work: the agent works on the PBIP project files and the user checks in Power BI Desktop.

## Contributing

Issues and pull requests are welcome: a rule that is wrong, a Power BI change the skills do not reflect yet, a new visual reference, a new skill. Start with [CONTRIBUTING.md](CONTRIBUTING.md) (repository layout, how to add a skill, versioning, checklist) and [AGENTS.md](AGENTS.md) (editing rules shared by all agents).

Examples that were not executed against a real model are listed under "To validate" in [CHANGELOG.md](CHANGELOG.md) — confirming one of them is a good first contribution.

Ideas for a **new Keemboll BI project**, beyond Power BI skills? Open a thread in the [organization discussions](https://github.com/Keemboll/.github/discussions).

## License

Apache 2.0 — see [LICENSE](LICENSE).
