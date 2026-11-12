# keemboll-bi

Skills pour **gérer et développer des projets BI avec Power BI / Microsoft Fabric** à l'aide d'un agent de code : du cadrage à l'exploitation, avec les règles maison de l'équipe.

- **Pour Claude Code** : une marketplace (`keemboll`) avec le plugin `keemboll-powerbi` — skills, sous-agents et guide intégré.
- **Pour les autres agents** (Codex, Grok, Gemini, Copilot, Cursor…) : les mêmes skills, au format ouvert *Agent Skills*, installés dans le projet BI par un script — voir [docs/agents.md](docs/agents.md).

> Les contenus marqués **« À ADAPTER »** sont des bonnes pratiques par défaut à remplacer par les règles réelles de l'équipe.

---

## Contenu

Le plugin `keemboll-powerbi` couvre tout le cycle d'un projet :

| Étape | Skill | Rôle |
|---|---|---|
| **Piloter** | `powerbi-project` | Phases d'un projet BI, fiche de cadrage `SCOPE.md`, catalogue de KPI `KPI.md`, rôles, definition of done |
| **Concevoir le modèle** | `powerbi-conventions` | Nommage, organisation du modèle, règles DAX de base, processus de validation avant modification |
| | `powerbi-data-modeling` | Modélisation dimensionnelle : schéma en étoile, grain, clés, SCD, dimensions de rôle, tables pont |
| | `powerbi-tmdl` | Lecture / écriture de modèles sémantiques au format TMDL (projets PBIP) |
| **Calculer** | `powerbi-dax-library` | Bibliothèque de mesures standard (time intelligence, marges, parts, classements…) |
| | `powerbi-performance` | Optimisation DAX et modèle (cardinalité, VertiPaq, Power Query, diagnostic) |
| **Construire le rapport** | `powerbi-mockup` | Maquette HTML d'une page à partir du modèle réel, avant de construire dans Power BI |
| | `powerbi-report-design` | Charte des rapports : thème, mise en page, accessibilité, choix des visuels |
| | `powerbi-html-visuals` | Visuels HTML / SVG générés en DAX (cartes, sparklines, barres de progression) |
| **Sécuriser** | `powerbi-governance` | RLS / OLS, étiquettes de sensibilité, endossement, accès et partage, fiche `SECURITY_MODEL.md` |
| **Vérifier** | `powerbi-testing` | Intégrité du modèle, rapprochement, tests de mesures, non-régression, tests RLS, recette (`tests/`) |
| | `powerbi-lean` | Revue de diff, audit (inutilisés, doublons, valeurs en dur), registre `DEBT.md` et journal `CHANGES.md` ; script `lean.py` |
| **Livrer** | `powerbi-alm` | Dépôt PBIP, branches, environnements, portes de qualité, intégration continue, mise en production |
| | `powerbi-documentation` | Dictionnaire de données `DATA_DICTIONARY.md` (généré), fiche de rapport, note de version, passation |

Sous-agents (Claude Code) : `powerbi-auditor` (relecture en lecture seule), `powerbi-modeler` (modèle et mesures), `powerbi-report-designer` (pages de rapport). Les mêmes rôles sont décrits dans `powerbi-project` pour les autres agents.

Guide d'utilisation intégré : dans Claude Code, tapez **`/keemboll-docs`** (ou `/keemboll-docs <section>` : installation, skills, exemples, projet, agents, lean, dette, methode, securite, depannage).

## Installation

### Claude Code

Prérequis : Claude Code, Azure CLI connecté (`az login --allow-no-subscriptions`), plugins Microsoft installés.

```powershell
# 1. Plugins Microsoft (source officielle)
claude plugin marketplace add microsoft/skills-for-fabric
claude plugin install fabric-skills@fabric-collection
claude plugin install powerbi-authoring@fabric-collection

# 2. Nos skills
claude plugin marketplace add keemboll/keemboll-bi
claude plugin install keemboll-powerbi@keemboll
```

Test local, avant de pousser sur GitHub :

```powershell
claude plugin marketplace add ./keemboll-bi
claude plugin install keemboll-powerbi@keemboll
```

Activer la mise à jour automatique : dans Claude Code, `/plugin` → **Marketplaces** → `keemboll` → **Enable auto-update** (idem pour `fabric-collection`).

### Codex, Grok, Gemini, Copilot, Cursor et autres

Prérequis : Python 3.8+ et une copie de ce dépôt.

```powershell
git clone https://github.com/keemboll/keemboll-bi
cd keemboll-bi
python scripts/install.py --agent codex --target "C:\chemin\vers\mon-projet-bi"   # ou grok, gemini, copilot, cursor, generic
```

Le script copie les skills dans le dossier que l'agent lit (`.agents/skills/`, `.grok/skills/`…) et ajoute au `AGENTS.md` du projet un bloc d'index des skills, sans toucher au reste du fichier. Relancer la commande met à jour ; `--uninstall` retire tout ; `--list` affiche les agents pris en charge. Pour un agent sans accès aux fichiers, `python scripts/build_dist.py` produit tous les skills en un seul fichier Markdown. Détails, emplacements et limites : [docs/agents.md](docs/agents.md).

## Structure

```
keemboll-bi/
├── .claude-plugin/
│   └── marketplace.json          # catalogue des plugins (marketplace « keemboll »), liste générée
├── plugins/
│   └── keemboll-powerbi/
│       ├── .claude-plugin/
│       │   └── plugin.json       # manifeste du plugin (version !)
│       ├── agents/               # sous-agents : auditeur, modeleur, concepteur de rapport
│       ├── commands/
│       │   └── keemboll-docs.md  # commande /keemboll-docs (guide)
│       └── skills/
│           └── <nom-du-skill>/
│               ├── SKILL.md      # instructions + frontmatter name/description
│               ├── references/   # détails chargés à la demande
│               └── scripts/      # scripts Python en lecture seule (lean.py)
├── scripts/
│   ├── validate.py               # contrôle de cohérence du dépôt
│   ├── install.py                # installation des skills pour un agent donné
│   ├── build_dist.py             # archives .zip et fichier unique dans dist/
│   ├── generate_marketplace.py   # régénère la liste des plugins
│   └── bump_versions.py          # incrément de version (CI)
├── tests/                        # tests des scripts + projet PBIP d'exemple (fixture)
├── docs/agents.md                # utilisation avec les autres agents
├── templates/skill-template/     # squelette de skill à copier
├── .claude/agents/               # rôles de maintenance du dépôt (rédaction, relecture, vérification, livraison)
├── AGENTS.md                     # règles pour éditer ce dépôt, communes à tous les agents
├── CLAUDE.md                     # importe AGENTS.md
└── CHANGELOG.md
```

Chaque skill n'existe qu'à un seul endroit (`plugins/<plugin>/skills/`). La liste `plugins` de `marketplace.json` est **générée automatiquement** depuis les `plugin.json` (`python scripts/generate_marketplace.py`) ; un workflow GitHub Actions (`.github/workflows/generate-marketplace.yml`), déclenché par le `push` sur `main`, la régénère et la commit si elle a changé. L'en-tête (`name`, `owner`, `metadata`) reste édité à la main. Un second workflow (`validate.yml`) lance la validation et les tests sur chaque demande de fusion et chaque branche.

## Ajouter ou modifier un skill

Les règles complètes sont dans [AGENTS.md](AGENTS.md).

1. Copier `templates/skill-template/` vers `plugins/keemboll-powerbi/skills/<nouveau-nom>/`.
2. Renseigner `name` (identique au nom du dossier, en kebab-case) et `description` (quand l'utiliser — c'est ce qui déclenche le skill).
3. Garder `SKILL.md` court (< 300 lignes) ; déplacer les détails dans `references/`. Écrire « l'agent », jamais le nom d'un produit.
4. Présenter le skill dans `plugins/keemboll-powerbi/commands/keemboll-docs.md` (sections `skills` et `exemples`) et dans le tableau ci-dessus.
5. **Version** : incrémentée automatiquement après le push (patch, `feat` → mineur, `!:` / `BREAKING CHANGE` → majeur) si tu ne l'as pas changée toi-même dans `plugin.json` ; `marketplace.json` est resynchronisé dans la foulée.
6. Ajouter une entrée dans `CHANGELOG.md`.
7. Valider puis publier :

```powershell
python scripts/validate.py
python -m unittest discover -s tests
git add .
git commit -m "feat(powerbi): <résumé>"
git push
```

Sans incrément de version, Claude Code ne voit pas la mise à jour.

## Coexistence avec les skills Microsoft

| Besoin | Skill Microsoft | Notre skill (appliqué en plus) |
|---|---|---|
| Modifier un modèle sémantique | `semantic-model-authoring` | `powerbi-conventions`, `powerbi-data-modeling`, `powerbi-tmdl` |
| Écrire des mesures | `semantic-model-authoring` | `powerbi-dax-library`, `powerbi-performance` |
| Créer / modifier un rapport | `powerbi-report-cli` | `powerbi-mockup`, `powerbi-report-design`, `powerbi-html-visuals` |
| Rôles de sécurité, étiquettes, endossement | `semantic-model-authoring`, `onelake-catalog-cli` | `powerbi-governance` |
| Promotion dev → test → prod, synchronisation Git | `deployment-pipelines-authoring-cli`, `git-integration-operations-cli` | `powerbi-alm` |
| Cadrage, tests et recette, documentation | — | `powerbi-project`, `powerbi-testing`, `powerbi-documentation` |
| Revue / audit / nettoyage d'un projet PBIP | — | `powerbi-lean` |
| Questions en langage naturel sur les données | `fabriciq` | — |

Les skills Microsoft gèrent la **mécanique** (API Fabric, fichiers PBIR / PBIP, MCP) ; les nôtres imposent les **règles maison**. En cas de contradiction, nos conventions priment sur les choix de style, jamais sur les contraintes techniques des API. Sans les skills Microsoft (autre agent, poste sans Azure CLI), nos skills restent utilisables : l'agent travaille sur les fichiers du projet PBIP et l'utilisateur vérifie dans Power BI Desktop.
