# Instructions for editing this repository

The repository rules are in `AGENTS.md`, shared by all agents:

@AGENTS.md

## Specific to Claude Code

- The maintenance roles in `.claude/agents/` are available as subagents (`skill-author`, `skill-reviewer`, `dax-verifier`, `docs-verifier`, `trend-scout`, `release-manager`). Write several skills in parallel with `skill-author`, then have them reviewed by `skill-reviewer`, `dax-verifier` and `docs-verifier`.
- To try the plugin as it will be installed: `claude plugin marketplace add ./` then `claude plugin install keemboll-powerbi@keemboll-bi`.
