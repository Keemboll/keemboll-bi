# Instructions for agents editing this repository

This file is authoritative for **all** agents (Claude Code, Codex, Grok, Gemini, Copilot, Cursor...). `CLAUDE.md` only imports it.

This repository (`keemboll-bi`) contains skills for running and developing BI projects with Power BI / Fabric. It complements `microsoft/skills-for-fabric`, which is never modified here. Skills follow the open **Agent Skills** format (a folder, a `SKILL.md`): they are published as a Claude Code marketplace and installed for other agents with `scripts/install.py`.

## Structure rules

- One skill = one folder `plugins/<plugin>/skills/<name>/` containing `SKILL.md` (+ optional `references/` and `scripts/`).
- Mandatory frontmatter: `name` (= folder name, kebab-case, ≤ 64 characters) and `description` (≤ 1024 characters, says **when** to use the skill, ends with `Triggers: ...` keywords).
- `SKILL.md` < 300 lines. Details go into `references/*.md`, cited by relative path from `SKILL.md`.
- A skill **never** references a file outside its plugin: only the plugin folder is copied at install time.
- No duplicated content between skills: point to the authoritative skill (e.g. "apply `powerbi-conventions`").
- One subagent = one file `plugins/<plugin>/agents/<name>.md` (frontmatter `name` = file name, `description`). It names the skills to apply and does not copy their rules.

## Portability across agents

- In a skill, write "the agent": never a product name, never a variable or path specific to one agent (`validate.py` flags it).
- A skill assumes no particular tool: cite the Microsoft skills or an MCP server as "when installed", and say what to do otherwise.
- Scripts shipped with a skill are Python (standard library) and are run by their path relative to the skill folder.
- Anything agent-specific lives outside the skills: the plugin's `commands/` and `agents/`, `.claude/`, `scripts/install.py`, `docs/agents.md`.

## Documentation

- Any skill added, renamed or changed in its usage must be reflected in `plugins/<plugin>/commands/<plugin>-docs.md` (sections `skills` and `examples`). `validate.py` rejects a skill missing from the guide.
- An agent supported in addition or no longer: update `scripts/install.py` (`AGENTS` table) and `docs/agents.md`.

## Versioning

- Any skill change ⇒ bump `version` (SemVer) in `plugins/<plugin>/.claude-plugin/plugin.json`, then `python scripts/generate_marketplace.py` to resync `.claude-plugin/marketplace.json` (otherwise the GitHub workflow does it after the push).
  - fix / rewording: patch (1.0.0 → 1.0.1)
  - new skill or new rule: minor (1.0.1 → 1.1.0)
  - rule removed or reversed: major (1.1.0 → 2.0.0)
- Add a dated entry to `CHANGELOG.md`.
- Run `python scripts/validate.py` and `python -m unittest discover -s tests` before every commit.
- Repository languages: **Python** (scripts, standard library only, 3.8+) and **Markdown**. No Node, no external dependency.

## Content

- Language: **English everywhere** — prose, code comments, object names in examples, file names.
- **No "ADAPT" markers.** A skill states a rule, or states a value as a *default* ("Default: 8 visuals per page"). A project overrides any default in its `TEAM_RULES.md` (mechanism owned by `powerbi-conventions`); skills do not repeat that mechanism, and `validate.py` rejects the marker.
- Never include tenant or workspace identifiers, tokens, real e-mails or customer data.
- Only state about Power BI / Fabric what is certain. For anything that moves (preview features, limits, UI labels), say so and point to the Microsoft documentation instead of asserting from memory.
- Example DAX and TMDL must be syntactically valid. An example that has not been executed is listed in the "To validate" section of `CHANGELOG.md`.

### Shared example model and vocabulary

All examples use the same model and the same names, so that skills read as one body of work:

| Kind | Names |
|---|---|
| Tables | `Fact_Sales`, `Fact_Budget`, `Dim_Customer`, `Dim_Product`, `Dim_Date`, `Dim_Store`, `_Measures`, `Param_*`, `CG_*` |
| Keys / columns | `CustomerKey`, `CustomerCode` (business key, stable across SCD2 versions), `ProductKey`, `Dim_Date[Date]`, `Fact_Sales[OrderDate]`, `Fact_Sales[DeliveryDate]`, `Fact_Sales[NetAmount]`, `Fact_Sales[Quantity]` |
| Measures | `[Net Sales]`, `[Net Sales PY]`, `[Net Sales YTD]`, `[Net Sales Change %]`, `[Gross Margin]`, `[Gross Margin %]`, `[Customer Count]`, `[Sales Target]` |
| Roles | `RLS_<scope>` (`RLS_Region`) |
| Project files | `SCOPE.md`, `KPI.md`, `TEAM_RULES.md`, `DATA_DICTIONARY.md`, `REPORT.md`, `RELEASE_NOTES.md`, `HANDOVER.md`, `SECURITY_MODEL.md`, `DEBT.md`, `CHANGES.md`, `RUNBOOK.md`, `MIGRATION.md`, `AI_INSTRUCTIONS.md`, `tests/ACCEPTANCE.md`, `tests/AI_QUESTIONS.md`, `incidents/I-001.md`, `mockups/<page>-v1.html` |
| Identifiers | `K-001` (KPI), `D-001` (debt), `C-001` (change), `T-001` (test), `I-001` (incident), `A-001` (migrated asset), `Q-01` (AI question), `VA-01` (verified answer) |
| `lean.py` subcommands | `audit`, `usage`, `debt`, `catalog` |
| Measure comment header | `// WHAT:` / `// HOW:` / `// NOTE:` |

## Maintenance roles

Role sheets in `.claude/agents/` — loaded as subagents by Claude Code, readable as plain instructions by any other agent:

| Role | File | When |
|---|---|---|
| Writing a skill | `.claude/agents/skill-author.md` | write or change a skill from a precise brief |
| Review | `.claude/agents/skill-reviewer.md` | independent opinion before commit (read-only) |
| Example code check | `.claude/agents/dax-verifier.md` | after adding or changing DAX / TMDL / M |
| Fact check | `.claude/agents/docs-verifier.md` | check Power BI / Fabric claims against the Microsoft documentation (read-only) |
| Watch | `.claude/agents/trend-scout.md` | list what changed in Power BI / Fabric and which skills it affects (read-only) |
| Release | `.claude/agents/release-manager.md` | version, changelog, guide, marketplace, validation |

The author of a skill is not its reviewer.
