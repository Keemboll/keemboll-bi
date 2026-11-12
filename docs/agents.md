# Utiliser les skills avec un autre agent que Claude Code

Les skills de ce dépôt suivent le format ouvert **Agent Skills** : un dossier par skill, un `SKILL.md` avec un frontmatter `name` / `description`, des `references/` chargées à la demande. Rien dans leur contenu ne dépend d'un agent particulier ; seul l'**emplacement** où l'agent les cherche change.

## Installation

Depuis une copie de ce dépôt, en visant le dossier du projet BI (celui qui contient le `.pbip`) :

```powershell
python scripts/install.py --agent codex   --target "C:\chemin\vers\mon-projet-bi"
python scripts/install.py --agent grok    --target "C:\chemin\vers\mon-projet-bi"
python scripts/install.py --agent gemini  --target "C:\chemin\vers\mon-projet-bi"
python scripts/install.py --list          # agents pris en charge et dossiers utilisés
```

Le script :

1. copie les skills dans le dossier attendu par l'agent ;
2. écrit dans `AGENTS.md` du projet un **bloc d'index** (entre deux marqueurs `keemboll-powerbi:début` / `keemboll-powerbi:fin`) qui dit quel `SKILL.md` lire avant quelle tâche — le reste du fichier n'est jamais touché ;
3. garde un manifeste (`.keemboll-powerbi-manifest.json`) pour pouvoir mettre à jour ou retirer proprement ce qu'il a installé, et seulement cela.

Relancer la même commande met à jour. `--uninstall` retire tout. `--dry-run` montre ce qui serait fait. `--global` installe dans le dossier personnel au lieu du projet. `--skills a,b` limite l'installation à certains skills. Un dossier de skill du même nom qui ne vient pas de ce script n'est jamais écrasé sans `--force`.

Les skills installés dans le projet sont à **versionner avec lui** : toute l'équipe — et la CI — utilise alors la même version des règles.

## Emplacements par agent

| Agent | `--agent` | Skills dans le projet | Skills personnels | Bloc `AGENTS.md` |
|---|---|---|---|---|
| Claude Code | `claude` | `.claude/skills/` (+ sous-agents dans `.claude/agents/`) | `~/.claude/skills/` | non (inutile) |
| Codex (OpenAI) | `codex` | `.agents/skills/` | `~/.agents/skills/` | oui |
| Gemini CLI | `gemini` | `.agents/skills/` | `~/.agents/skills/` | oui |
| Grok Build (xAI) | `grok` | `.grok/skills/` | `~/.grok/skills/` | oui |
| GitHub Copilot (VS Code) | `copilot` | `.github/skills/` | `~/.copilot/skills/` | oui |
| Cursor | `cursor` | `.cursor/skills/` | `~/.cursor/skills/` | oui |
| Autre agent | `generic` | `.agents/skills/` | `~/.agents/skills/` | oui |

> **À VÉRIFIER** — ces emplacements ont été relevés dans la documentation des éditeurs en novembre 2026 et changent d'une version à l'autre. Celui de Cursor au niveau du projet n'a pas pu être confirmé. En cas de doute, consulter la documentation de l'agent et imposer le dossier avec `--dest <dossier>`.

Pour Claude Code, préférer la marketplace (mises à jour automatiques, commande `/keemboll-docs`, sous-agents) — voir le `README.md`. D'après la documentation de xAI, Grok Build sait aussi lire les marketplaces et plugins Claude Code tels quels.

## Agent sans chargement de skills

Deux solutions de repli, de la meilleure à la plus simple :

1. **L'agent lit `AGENTS.md` et les fichiers du projet** : `--agent generic` suffit. Le bloc d'index lui demande de lire le `SKILL.md` concerné avant d'agir ; c'est l'équivalent manuel du chargement automatique.
2. **L'agent n'a pas accès aux fichiers** (conversation web, assistant dans un navigateur) : `python scripts/build_dist.py` produit `dist/keemboll-powerbi-<version>.md`, tous les skills en un seul fichier à joindre à la conversation ou à un projet. Les scripts (`lean.py`) n'y sont pas utilisables.

`build_dist.py` produit aussi un `.zip` par skill et un `.zip` de l'ensemble, pour les applications qui acceptent le téléversement d'un skill.

## Ce qui reste propre à Claude Code

| Élément | Emplacement | Équivalent ailleurs |
|---|---|---|
| Commande `/keemboll-docs` | `plugins/keemboll-powerbi/commands/` | lire ce fichier et le `README.md` |
| Sous-agents `powerbi-auditor`, `powerbi-modeler`, `powerbi-report-designer` | `plugins/keemboll-powerbi/agents/` | les mêmes rôles sont décrits dans le skill `powerbi-project` (table rôle → skills) ; les fiches sont de simples fichiers Markdown, lisibles comme consignes |
| Skills Microsoft (`semantic-model-authoring`, `powerbi-report-cli`…) et serveur MCP de modélisation | marketplace `microsoft/skills-for-fabric` | nos skills les citent comme « s'ils sont installés » ; sans eux, l'agent édite les fichiers TMDL / PBIR du projet PBIP directement et l'utilisateur vérifie dans Power BI Desktop |

## Vérifier l'installation

Dans le projet BI, demander à l'agent : « Quels skills Power BI as-tu à disposition, et lequel appliques-tu avant de renommer une mesure ? » Il doit citer `powerbi-conventions` et `powerbi-lean` (inventaire `usage` avant renommage). S'il ne les connaît pas, vérifier le dossier d'installation (`--list`) et la présence du bloc dans `AGENTS.md`.

## Sécurité

Quel que soit l'agent : les **métadonnées** du projet (noms, DAX, rôles) partent chez son fournisseur dès qu'il les lit. Vérifier que l'outil est autorisé pour ce projet avant de l'ouvrir — règle détaillée dans `powerbi-conventions` et `powerbi-governance`.
