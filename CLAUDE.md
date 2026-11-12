# Instructions pour éditer ce dépôt

Les règles du dépôt sont dans `AGENTS.md`, commun à tous les agents :

@AGENTS.md

## Propre à Claude Code

- Les rôles de maintenance de `.claude/agents/` sont disponibles comme sous-agents (`skill-author`, `skill-reviewer`, `dax-verifier`, `release-manager`). Rédiger plusieurs skills en parallèle avec `skill-author`, puis faire relire par `skill-reviewer` et `dax-verifier`.
- Pour essayer le plugin tel qu'il sera installé : `claude plugin marketplace add ./` puis `claude plugin install keemboll-powerbi@keemboll-bi`.
