# Using the skills with an agent other than Claude Code

The skills of this repository follow the open **Agent Skills** format: one folder per skill, a `SKILL.md` with a `name` / `description` frontmatter, `references/` loaded on demand. Nothing in their content depends on a particular agent; only the **folder** where the agent looks for them changes.

## Installation

From a copy of this repository, targeting the BI project folder (the one that contains the `.pbip`):

```powershell
python scripts/install.py --agent codex   --target "C:\path\to\my-bi-project"
python scripts/install.py --agent grok    --target "C:\path\to\my-bi-project"
python scripts/install.py --agent gemini  --target "C:\path\to\my-bi-project"
python scripts/install.py --list          # supported agents and folders used
```

The script:

1. copies the skills into the folder the agent expects;
2. writes into the project's `AGENTS.md` an **index block** (between two markers `keemboll-powerbi:begin` / `keemboll-powerbi:end`) that says which `SKILL.md` to read before which task — the rest of the file is never touched;
3. keeps a manifest (`.keemboll-powerbi-manifest.json`) so that it can update or remove cleanly what it installed, and only that.

Running the same command again updates. `--uninstall` removes everything. `--dry-run` shows what would be done. `--global` installs into the home folder instead of the project. `--skills a,b` limits the installation to some skills. A skill folder of the same name that does not come from this script is never overwritten without `--force`.

Skills installed in the project are meant to be **versioned with it**: the whole team — and the CI — then uses the same version of the rules.

## Folders per agent

| Agent | `--agent` | Skills in the project | Personal skills | `AGENTS.md` block |
|---|---|---|---|---|
| Claude Code | `claude` | `.claude/skills/` (+ subagents in `.claude/agents/`) | `~/.claude/skills/` | no (not needed) |
| Codex (OpenAI) | `codex` | `.agents/skills/` | `~/.agents/skills/` | yes |
| Gemini CLI | `gemini` | `.agents/skills/` | `~/.agents/skills/` | yes |
| Grok Build (xAI) | `grok` | `.grok/skills/` | `~/.grok/skills/` | yes |
| GitHub Copilot (VS Code) | `copilot` | `.github/skills/` | `~/.copilot/skills/` | yes |
| Cursor | `cursor` | `.cursor/skills/` | `~/.cursor/skills/` | yes |
| Other agent | `generic` | `.agents/skills/` | `~/.agents/skills/` | yes |

These folders come from each vendor's documentation as of November 2026 and change between versions. If an agent does not pick the skills up, check its current documentation and force the folder with `--dest <folder>`; the `AGENTS.md` index block works as a fallback in every case.

For Claude Code, prefer the marketplace (automatic updates, `/keemboll-docs` command, subagents) — see `README.md`. According to xAI's documentation, Grok Build can also read Claude Code marketplaces and plugins as they are.

## Agent that does not load skills

Two fallbacks, from best to simplest:

1. **The agent reads `AGENTS.md` and the project files**: `--agent generic` is enough. The index block asks it to read the relevant `SKILL.md` before acting; it is the manual equivalent of automatic loading.
2. **The agent has no file access** (web chat, browser assistant): `python scripts/build_dist.py` produces `dist/keemboll-powerbi-<version>.md`, all the skills in a single file to attach to the conversation or to a project. The scripts (`lean.py`) cannot be used there.

`build_dist.py` also produces one `.zip` per skill and one `.zip` of the whole set, for applications that accept uploading a skill.

## What remains specific to Claude Code

| Element | Location | Equivalent elsewhere |
|---|---|---|
| `/keemboll-docs` command | `plugins/keemboll-powerbi/commands/` | read that file and `README.md` |
| Subagents `powerbi-analyst`, `powerbi-modeler`, `powerbi-report-designer`, `powerbi-tester`, `powerbi-ai-curator`, `powerbi-ops`, `powerbi-auditor` | `plugins/keemboll-powerbi/agents/` | the same roles are described in the `powerbi-project` skill (role → skills table); the files are plain Markdown, readable as instructions by any agent |
| Microsoft skills (`semantic-model-authoring`, `powerbi-report-cli`...) and the modeling MCP server | marketplace `microsoft/skills-for-fabric` | our skills cite them as "when installed"; without them, the agent edits the TMDL / PBIR files of the PBIP project directly and the user checks in Power BI Desktop |

## Checking the installation

In the BI project, ask the agent: "Which Power BI skills do you have, and which one do you apply before renaming a measure?" It should name `powerbi-conventions` and `powerbi-lean` (`usage` inventory before a rename). If it does not know them, check the install folder (`--list`) and the block in `AGENTS.md`.

## Security

Whatever the agent: the project's **metadata** (names, DAX, roles) goes to its provider as soon as it reads it. Check that the tool is allowed for this project before opening it — rule detailed in `powerbi-conventions` and `powerbi-governance`.
