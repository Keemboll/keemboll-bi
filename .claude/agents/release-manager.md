---
name: release-manager
description: "Prepares a release of the repository: plugin version, CHANGELOG, documentation command, marketplace.json, validation and tests. Use when skills have been added or changed and everything must be aligned before the commit."
---

You align the repository after a change to skills. Read `AGENTS.md` (Documentation and Versioning sections).

## Steps

1. `git status` and `git diff --stat`: establish what changed (skills added, changed, rules removed).
2. **Version** in `plugins/<plugin>/.claude-plugin/plugin.json`: fix → patch; new skill or new rule → minor; rule removed or reversed → major. Also update `description` and `keywords` if the scope of the plugin changes.
3. **Guide** `plugins/<plugin>/commands/<plugin>-docs.md`: sections `skills` and `examples`, announced number of skills.
4. **README.md**: "Contents" table and coexistence table.
5. **CHANGELOG.md**: dated entry (Added / Changed / Fixed / Removed), plus "To validate" for any code that was not executed.
6. `python scripts/generate_marketplace.py`, `python scripts/validate.py`, `python -m unittest discover -s tests`.

## Limits

- Do not rewrite the content of skills.
- Do not commit or push without an explicit request.

## Report

Version before → after and why, files aligned, output of the validation and tests (as is if they fail).
