# Changelog

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) — versioning: [SemVer](https://semver.org/).

## [2.0.1] — 2026-11-13

### Changed
- The guide command is now **`/keemboll-bi-docs`** (was `/keemboll-docs`), matching the marketplace name. File renamed to `commands/keemboll-bi-docs.md`; README, `docs/agents.md` and `CONTRIBUTING.md` updated.

## [2.0.0] — 2026-11-13

The repository becomes an English-only, community-ready toolkit, and the plugin grows from 14 to 20 skills to cover the current Power BI / Fabric landscape: AI readiness, DAX user-defined functions, Power Query, Direct Lake, operations and migration.

### Added
- Skill **`powerbi-ai-readiness`**: preparing a semantic model for Copilot and Fabric data agents — model hygiene, AI data schema, verified answers, AI instructions (`AI_INSTRUCTIONS.md`), AI question set (`tests/AI_QUESTIONS.md`), test protocol and "Approved for Copilot" gate.
- Skill **`powerbi-dax-udf`**: DAX user-defined functions (generally available since June 2026, compatibility level 1702+) — when to use them, namespaced naming, parameter types and passing modes, `functions.tmdl`, `DEFINE FUNCTION` tests, migration of duplicated measures; six ready-made functions.
- Skill **`powerbi-power-query`**: M code — where a transformation belongs, query organisation (`stg_`, `p`, `fn`), parameters, query folding, typing and errors, incremental refresh (`RangeStart` / `RangeEnd`), privacy levels; patterns, folding guide, review checklist.
- Skill **`powerbi-direct-lake`**: storage mode decision, Direct Lake on OneLake vs on SQL analytics endpoint, framing and transcoding, guardrails, fallback and `DirectLakeBehavior`, security, Delta table hygiene, Import → Direct Lake migration.
- Skill **`powerbi-operations`**: after go-live — what to watch and where, refresh failure triage, incident process and severity scale (`incidents/I-xxx.md`), capacity watch, usage and retirement of unused content, `RUNBOOK.md`, health review checklist.
- Skill **`powerbi-migration`**: PBIX → PBIP and other format moves, Tableau / Qlik / Excel and Power Pivot / SSRS / Looker / SSAS → Power BI — seven-step method, concept mapping tables, parity and cut-over, `MIGRATION.md`.
- `powerbi-dax-library`: calendar-based time intelligence (`calendar-time-intelligence.md`, preview) and visual calculations (`visual-calculations.md`).
- `powerbi-alm`: code-first promotion with fabric-cicd (`fabric-cicd.md`) as a third route next to deployment pipelines and Git integration.
- `powerbi-tmdl`: `functions.tmdl` and the TMDL form of a user-defined function.
- Plugin subagents: `powerbi-analyst` (scoping), `powerbi-tester` (tests and acceptance), `powerbi-ai-curator` (AI readiness), `powerbi-ops` (operations).
- Maintenance roles in `.claude/agents/`: `docs-verifier` (fact-check against the Microsoft documentation) and `trend-scout` (monthly watch of Power BI / Fabric changes mapped to the skills).
- `validate.py`: rejects ADAPT markers and French text in skills.
- `AGENTS.md`: shared example model and vocabulary (tables, measures, project files, identifiers) used by every skill.

### Changed
- **Everything is in English**: skills, references, templates, subagents, guide, README, scripts, workflows. Example objects use one shared model (`Fact_Sales`, `Dim_Customer`, `Dim_Product`, `Dim_Date`, `[Net Sales]`).
- **No more "À ADAPTER" markers**: each value is stated as a default. `TEAM_RULES.md` (owned by `powerbi-conventions`) is the single place where a team overrides defaults; its template now lists every default of the plugin.
- Measure comment header: `// WHAT:` / `// HOW:` / `// NOTE:` (was QUOI / COMMENT / ADAPTER).
- Change-log identifiers in `CHANGES.md`: `C-xxx` (was `M-xxx`); commit message `C-xxx: <summary>`.
- `lean.py` subcommands documented as `audit`, `usage`, `debt`, `catalog` (the script already used these names); `usage` labels a visual without type as `visual`.
- `powerbi-project`: the six new skills wired into the phases (Power Query and Direct Lake in modeling, UDFs in measures, AI readiness as an optional release gate, operations authoritative in phase 8, migration in the takeover process); seven subagents in the roles table.
- `powerbi-data-modeling`: storage-mode table reduced to a summary; `powerbi-direct-lake` and `powerbi-power-query` are authoritative for the details. Only Direct Lake on OneLake combines with Import tables.
- `powerbi-performance`: points to `powerbi-power-query` for M and incremental refresh, and to `powerbi-direct-lake`.
- `powerbi-governance`: exposure to Copilot and data agents points to `powerbi-ai-readiness`.
- `validate.py`: "Copilot" alone is the Power BI feature and is no longer flagged; only "GitHub Copilot" counts as a coding agent.
- Template `templates/skill-template/`: English, `references/example.md`.

### Removed
- The "À ADAPTER" convention (rule reversed, hence the major version).

### To validate
No DAX engine, Power BI Desktop or Fabric workspace was available: nothing below has been executed. Examples were reviewed by reading and against Microsoft Learn where noted in each skill.
- Every DAX example renamed during the translation: `powerbi-dax-library` (all references, including the `DATATABLE` toggles of `switches.md` and the new `Sales Target`), `powerbi-performance` (`dax-anti-patterns.md`), `powerbi-testing` (`check-queries.md`), `powerbi-governance` (`rls-ols.md`), `powerbi-html-visuals` (SVG / HTML templates), `powerbi-conventions` (`Net Sales Change %`).
- `powerbi-dax-library`: the four calendar-based measures and the TMDL calendar block (`calendar-time-intelligence.md`); the six visual calculations (`visual-calculations.md`).
- `powerbi-dax-udf`: `Period.PriorYearVal` / `Period.PriorYearExpr`, the six functions of `patterns.md` and their calling measures, the `functions.tmdl` block (quoting of dotted names and indentation not confirmed on a file saved by Desktop), the test queries and `INFO.USERDEFINEDFUNCTIONS()` / `INFO.FUNCTIONS`.
- `powerbi-tmdl`: the `AddTax` function in `syntax.md` (file-level indentation with tabs).
- `powerbi-power-query`: all M patterns of `m-patterns.md`, the `Value.NativeQuery` example of `query-folding.md`, the `CommandTimeout` snippet; whether a `Date.From ( RangeStart )` filter folds.
- `powerbi-direct-lake`: `EVALUATE TABLETRAITS ()` and the `Sql.Database` → `AzureStorage.DataLake` expression change.
- `powerbi-operations`: the duplicate-key query of `refresh-triage.md` and the five `INFO.VIEW.*` queries of `health-review-checklist.md`.
- `powerbi-migration`: the seven DAX patterns of `mapping-tableau.md` and `mapping-qlik.md` (patterns to test, not guaranteed equivalents).
- `powerbi-alm`: the `parameter.yml` example of `fabric-cicd.md`; the GitHub Actions and Azure DevOps workflows of `ci-examples.md` (the `ci_threshold.py` helper was run against real `lean.py` output).
- `powerbi-mockup`: the template was parsed, not opened in a browser.
- Product facts to re-check regularly (`docs-verifier`): the legacy Q&A retirement date (sources say December 2026 or February 2027), "Detect and reload external PBIP changes" and Desktop Bridge labels, OLS combined with RLS, Direct Lake guardrails and default behaviours, PBIR as the default report format.

## [1.6.0] — 2026-11-11

The plugin moves from "rules to build a model and a report" to running a BI project end to end, and opens up to agents other than Claude Code.

### Added
- Skill **`powerbi-project`**: phases of a BI project (scoping → operations), deliverable and exit criterion of each phase, authoritative skill, `SCOPE.md` brief, `KPI.md` catalog, roles, definition of done.
- Skill **`powerbi-governance`**: static and dynamic RLS, OLS, sensitivity labels, endorsement, workspace roles, sharing, personal data, `SECURITY_MODEL.md`.
- Skill **`powerbi-testing`**: six test levels (integrity, reconciliation, measures, non-regression, RLS, report), DAX check queries, `tests/` folder and `tests/ACCEPTANCE.md` record.
- Skill **`powerbi-alm`**: PBIP repository, `.gitignore`, branches and commits, environments, deployment pipelines vs Git integration, quality gates, CI examples (GitHub Actions, Azure DevOps), versions and rollback.
- Skill **`powerbi-documentation`**: generated data dictionary, report sheet, release notes, handover.
- `lean.py catalog`: data dictionary in Markdown (or `--json`) on standard output, from the TMDL and the report; an RLS filter containing an e-mail address is not copied.
- Plugin subagents: `powerbi-auditor` (read-only), `powerbi-modeler`, `powerbi-report-designer`.
- **Other agents**: `scripts/install.py` installs the skills into a BI project for Codex, Grok, Gemini, Copilot, Cursor or any agent that reads `AGENTS.md` (skill copy, index block in `AGENTS.md`, clean update and uninstall); `scripts/build_dist.py` builds one `.zip` per skill, one `.zip` of the set and all skills in a single Markdown file; guide `docs/agents.md`.
- `AGENTS.md` becomes the source of the repository rules for all agents ("Portability across agents" section); `CLAUDE.md` imports it.
- Maintenance roles in `.claude/agents/`: `skill-author`, `skill-reviewer`, `dax-verifier`, `release-manager`.
- `validate.py`: checks subagents, relative links of every Markdown file of a skill (broken or outside the plugin), cited skills that do not exist; warning when a `SKILL.md` names a specific agent.
- Tests (`tests/`, `python -m unittest discover -s tests`) of the repository scripts and of `lean.py` on a sample PBIP project; `validate.yml` workflow on every pull request and every branch.
- `/keemboll-docs`: `project` and `agents` sections, 14 skills, new example requests.

### Changed
- `powerbi-conventions`: the "Security and governance" section points to `powerbi-governance` for role design.
- `powerbi-report-design` (`svg-backgrounds.md`): agent-independent wording.
- `README.md`: contents by project stage, installation for other agents.

### To validate
No DAX engine was available: nothing below was executed.
- DAX check queries of `powerbi-testing` (`check-queries.md`).
- TMDL and DAX examples of RLS / OLS roles in `powerbi-governance` (`rls-ols.md`).
- GitHub Actions and Azure DevOps workflows of `powerbi-alm` (`ci-examples.md`): YAML reviewed, never run.
- Skill folders per agent (`docs/agents.md`): taken from the vendors' documentation, not tested with each agent; Cursor's project-level folder is not confirmed.
- `lean.py catalog`: tested on the sample project `tests/fixture/Demo` only.

## [1.5.1] — 2026-10-27

### Fixed
- `powerbi-tmdl`, `powerbi-report-design`, `/keemboll-docs`: **reloading external changes** (preview, Desktop August 2026 or later, option *Detect and reload external PBIP changes*) and the **Desktop Bridge** (Options → Security, on by default; also documented as preview) are now two distinct mechanisms.
- `powerbi-data-modeling`, `powerbi-performance`: **Direct Lake on OneLake** (recommended for new models; no DirectQuery fallback; composite possible; calculated columns in user context in preview; guardrails exceeded = query error) distinguished from **Direct Lake on SQL analytics endpoint** (DirectQuery fallback, `DirectLakeBehavior`).
- `powerbi-performance`: `SWITCH` stops at the first matching value; the field parameter / calculation group advice is about usability, not performance.
- Number of visuals per page aligned: 6 to 8 (`powerbi-report-design`) and at most 8 (`powerbi-performance`), presented as a house heuristic.
- `powerbi-dax-library`: 3-month moving average (`CALCULATE` around `AVERAGEX`, behaviour of empty months documented); `_dateMax` replaced by a last-sales-date measure; new / lost customers through `SUMMARIZE` on `CustomerCode` (SCD2); share of category at every level under the category; fiscal YTD added.
- `powerbi-performance` (anti-patterns §2 and §6): `CustomerCode` instead of `CustomerKey`, with an SCD2 note.
- `powerbi-data-modeling` (`dim-date.md`): date table bounds computed on both order and delivery dates.

### To validate
No DAX engine was available (no Tabular Editor CLI, DAX Studio or modeling MCP server): these measures were **not** executed — 3-month moving average, fiscal YTD, new customers, lost customers, share of category, the two measures of the anti-patterns reference, the DAX `Dim_Date` with delivery date.

## [1.5.0] — 2026-10-16

### Added
- **`/keemboll-docs [section]`** command: user guide of the plugin (installation, skills, example requests, `lean.py`, debt and change log, method, security, troubleshooting).
- `validate.py`: checks that every skill is presented in the documentation command and that every command has a frontmatter.

## [1.4.1] — 2026-10-16

### Added
- `powerbi-lean`: procedure to initialise `CHANGES.md` on a project that already has debt (from the Git history, inventing nothing).
- Partial reference in the change log (`D-xxx (partial)` / `(in progress)`): progress that does not close the debt, accepted by `lean.py debt`.

## [1.4.0] — 2026-10-15

### Added
- `powerbi-lean`: **`CHANGES.md`** change log (template `changes-template.md`) that fills up as the debt goes down; "close a debt" procedure (change entry, debt moved to "Closed", one commit).
- `lean.py debt`: state of the debt (open / closed, progress, priorities, overdue items), next identifiers and consistency check between `DEBT.md` and `CHANGES.md`.

### Changed
- `debt-template.md`: a closed debt points to its change entry instead of a commit hash.

## [1.3.0] — 2026-10-14

### Changed
- `powerbi-lean`: the audit script moves from Node (`lean.mjs`) to **Python** (`lean.py`, 3.8+, standard library only). Same commands (`audit`, `usage`, `--changed`, `--field`, `--json`) and same results, checked on a sample project and a test set.
- Console output forced to UTF-8 (Windows); deterministic order of results.
- Repository scripts moved to Python (standard library): `validate.py`, `generate_marketplace.py` (byte-identical output), `bump_versions.py`; the GitHub Actions workflow uses `setup-python`. The repository now contains only Python and Markdown.

### Removed
- `lean.mjs` (replaced by `lean.py`).
- `scripts/*.mjs` and `package.json` (replaced by the Python scripts).

## [1.2.0] — 2026-10-13

### Added
- Skill `powerbi-lean` ("fewer objects, not less documentation"): `review` (git diff), `audit` (whole project) and `debt` (`DEBT.md` register outside the model) modes.
- Script `powerbi-lean/scripts/lean.mjs` (Node, no dependency, read-only): TMDL + PBIR audit (unused objects, duplicates, hard-coded values, FILTER on a table, summarizeBy, visible keys, date table), `--changed` option, and `usage` to inventory the fields in use before a rename.

## [1.1.0] — 2026-10-13

Inspired by the guide "How I Build Power BI Reports with AI" (L. Reese).

### Added
- Skill `powerbi-mockup`: HTML mockup of a page from the real model (labelled fields, missing measures listed, iterations, move to PBIP) with template and checklist.
- `powerbi-report-design`: four questions per page, quantified design tokens, Z layout with toggles, visual check by screenshot, "5 problems" review, SVG page backgrounds, reusable visual references (entry template and a first "KPI comparison card" reference).
- `powerbi-dax-library`: toggles through disconnected tables (Plan / PY, Top / Bottom, Monthly / Cumulative), dynamic titles and colours.
- `powerbi-conventions`: "existing model vs new model" rules, metadata confidentiality (health and personal data), three-line comment in measures, Git mandatory before writing.

### Changed
- `powerbi-conventions`: `DIVIDE(a, b, 0)` ≠ `COALESCE(DIVIDE(a, b), 0)`.
- `powerbi-tmdl`: synchronisation with Desktop (save first, apply external changes or Desktop Bridge) instead of "close Desktop".

## [Unreleased] — 2026-10-13

### Added
- Automatic version bump of a changed plugin (level derived from the commit messages).
- Generation of the `plugins` list of `marketplace.json` from the `plugin.json` files, with a check mode.
- GitHub Actions workflow `generate-marketplace.yml` (`push` to `main`): regenerates and commits `marketplace.json`.

## [1.0.0] — 2026-10-13

### Added
- `keemboll-bi` marketplace and `keemboll-powerbi` plugin.
- Skills: `powerbi-conventions`, `powerbi-data-modeling`, `powerbi-tmdl`, `powerbi-dax-library`, `powerbi-performance`, `powerbi-report-design`, `powerbi-html-visuals`.
- Skill template (`templates/skill-template/`) and validation script.
