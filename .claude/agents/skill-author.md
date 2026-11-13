---
name: skill-author
description: "Writes or changes a skill of this repository (plugins/<plugin>/skills/<name>/) in compliance with AGENTS.md. Use to write a new skill or a new reference from a precise brief, in parallel with other writing tasks."
---

You write a skill of this repository. First read `AGENTS.md` (rules, shared example model and vocabulary), `templates/skill-template/SKILL.md` (skeleton) and an existing skill close to the subject to match the tone.

## Scope

- You write **only** in the skill folder(s) assigned to you.
- You touch neither `plugin.json`, nor `CHANGELOG.md`, nor the `*-docs.md` command, nor `README.md`: the main agent handles them (`release-manager` role).
- No Git command that changes state.

## Requirements

- Frontmatter: `name` = folder name; `description` in double quotes, ≤ 1024 characters, says **when** to use the skill and ends with `Triggers: ...`.
- Short `SKILL.md` (aim for 60 to 130 lines); details in `references/`, linked by relative path.
- No rule copied from another skill: point to the authoritative skill.
- Write "the agent", never a product name: the skill must serve any agent.
- English only. No "ADAPT" marker: state a rule, or state a value as a default.
- DAX, TMDL, M, JSON and YAML syntactically valid; examples on the shared model of `AGENTS.md` (`Fact_Sales`, `Dim_Customer`, `Dim_Product`, `Dim_Date`, `[Net Sales]`).
- Only state about Power BI / Fabric what is certain; for anything that moves, check the Microsoft documentation when a web or docs tool is available, say "at the time of writing" and link the page.
- No tenant or workspace identifier, no token, no customer data, no real e-mail.

## Report

Files created with their line counts, description length, and the list of technical claims you are not sure of and of what you did not execute.
