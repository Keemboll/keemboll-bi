# Contributing to keemboll-bi

Thanks for helping improve `keemboll-bi`! This file covers what is specific to this repository. The general Keemboll guidelines (scope, quality bar, how to propose a new project, security reporting) are in the [organization contributing guide](https://github.com/Keemboll/.github/blob/main/CONTRIBUTING.md) and apply here too.

Two documents govern how this repository is edited — read them before your first pull request:

- **[AGENTS.md](AGENTS.md)** — the authoritative editing rules, shared by humans and by every coding agent (structure, portability, versioning, content, shared example model).
- **[CHANGELOG.md](CHANGELOG.md)** — what changed, and the list of examples still "To validate".

## Ways to contribute

- **Fix a rule** that is wrong or outdated for current Power BI / Fabric.
- **Add or improve a skill**, a reference, a template or a subagent.
- **Validate an example**: items under "To validate" in the changelog were not executed against a real model — confirming one (or correcting it) is a good first contribution.
- **Report what happened on your project**: a skill that triggered wrongly, a rule that did not hold, a missing case.
- **Improve the docs**: `README.md`, `docs/agents.md`, the `/keemboll-bi-docs` guide.

For anything larger than a small fix, open an issue first so we agree on the approach.

## Development setup

Requirements: Git and Python 3.8+ (standard library only — no Node, no external dependency).

```powershell
git clone https://github.com/Keemboll/keemboll-bi
cd keemboll-bi
git checkout -b my-change
```

Before every commit:

```powershell
python scripts/validate.py
python -m unittest discover -s tests
```

The `validate` workflow runs the same checks on every pull request and every branch; it must pass before review.

## Repository layout

```
keemboll-bi/
├── .claude-plugin/
│   └── marketplace.json          # plugin catalog ("keemboll-bi" marketplace), list generated
├── plugins/
│   └── keemboll-powerbi/
│       ├── .claude-plugin/
│       │   └── plugin.json       # plugin manifest (version!)
│       ├── agents/               # subagents: analyst, modeler, report designer, tester, AI curator, ops, auditor
│       ├── commands/
│       │   └── keemboll-bi-docs.md  # /keemboll-bi-docs command (guide)
│       └── skills/
│           └── <skill-name>/
│               ├── SKILL.md      # instructions + name/description frontmatter
│               ├── references/   # details loaded on demand
│               └── scripts/      # read-only Python scripts (lean.py)
├── scripts/
│   ├── validate.py               # repository consistency check
│   ├── install.py                # installs the skills for a given agent
│   ├── build_dist.py             # .zip archives and single file in dist/
│   ├── generate_marketplace.py   # regenerates the plugin list
│   └── bump_versions.py          # version bump (CI)
├── tests/                        # script tests + sample PBIP project (fixture)
├── docs/agents.md                # use with other agents
├── templates/skill-template/     # skill skeleton to copy
├── .claude/agents/               # maintenance roles (author, reviewer, DAX check, docs check, trend watch, release)
├── AGENTS.md                     # rules for editing this repository, shared by all agents
├── CLAUDE.md                     # imports AGENTS.md
└── CHANGELOG.md
```

Each skill exists in one place only (`plugins/<plugin>/skills/`). The `plugins` list of `marketplace.json` is **generated** from the `plugin.json` files (`python scripts/generate_marketplace.py`); a GitHub Actions workflow (`.github/workflows/generate-marketplace.yml`), triggered by a push to `main`, regenerates and commits it when it changed. The header (`name`, `owner`, `metadata`) is edited by hand. A second workflow (`validate.yml`) runs the validation and the tests on every pull request and every branch.

## Adding or changing a skill

The full rules are in [AGENTS.md](AGENTS.md).

1. Copy `templates/skill-template/` to `plugins/keemboll-powerbi/skills/<new-name>/`.
2. Fill in `name` (same as the folder name, kebab-case) and `description` (when to use it — this is what triggers the skill).
3. Keep `SKILL.md` short (< 300 lines); move details into `references/`. Write "the agent", never a product name. English only.
4. Present the skill in `plugins/keemboll-powerbi/commands/keemboll-bi-docs.md` (sections `skills` and `examples`) and in the table above.
5. **Version**: bumped automatically after the push (patch, `feat` → minor, `!:` / `BREAKING CHANGE` → major) if you did not change it yourself in `plugin.json`; `marketplace.json` is resynced along the way.
6. Add an entry to `CHANGELOG.md`.
7. Validate, then publish:

```powershell
python scripts/validate.py
python -m unittest discover -s tests
git add .
git commit -m "feat(powerbi): <summary>"
git push
```

Without a version bump, Claude Code does not see the update.

## Quality bar

On top of the [organization quality bar](https://github.com/Keemboll/.github/blob/main/CONTRIBUTING.md#quality-bar-all-projects):

- **Only state what is certain** about Power BI / Fabric. For anything that moves (preview features, limits, UI labels), say so and point to the Microsoft documentation.
- **DAX, TMDL and M examples must be syntactically valid.** An example not executed against a real model goes under "To validate" in the changelog.
- **English everywhere**: prose, comments, object names, file names.
- **Portable**: write "the agent", never a product name; agent-specific content lives outside the skills (`commands/`, `agents/`, `.claude/`, `scripts/install.py`, `docs/agents.md`).
- **No tenant or workspace identifiers, tokens, real e-mails or customer data**, even in examples.
- **The author of a skill is not its reviewer.** The `.claude/agents/` role sheets (author, reviewer, DAX check, docs check, trend watch, release) describe the process.

## Pull request checklist

- [ ] `python scripts/validate.py` and `python -m unittest discover -s tests` pass
- [ ] The change is focused and explained in the PR description
- [ ] New or renamed skill: reflected in `commands/keemboll-bi-docs.md` and in the README table
- [ ] `CHANGELOG.md` has a dated entry; unexecuted examples are listed under "To validate"
- [ ] Version handled: bumped in `plugin.json`, or left to the automatic bump (commit prefix)
- [ ] `marketplace.json` untouched by hand (the plugin list is generated)
- [ ] No secrets or private data

## Security

Do not open a public issue for a security problem. Use GitHub's private vulnerability reporting (repository **Security** tab → *Report a vulnerability*) or contact the maintainer directly.

## Questions and ideas

Open an issue, or use the [organization discussions](https://github.com/Keemboll/.github/discussions) for broader ideas, including proposals for new Keemboll BI projects.
