# Instructions pour les agents qui éditent ce dépôt

Ce fichier fait foi pour **tous** les agents (Claude Code, Codex, Grok, Gemini, Copilot, Cursor…). `CLAUDE.md` ne fait que l'importer.

Ce dépôt (`keemboll`) contient des skills pour la gestion et le développement de projets BI avec Power BI / Fabric. Il complète `microsoft/skills-for-fabric`, qui n'est jamais modifié ici. Les skills suivent le format ouvert **Agent Skills** (un dossier, un `SKILL.md`) : ils sont publiés comme marketplace Claude Code et s'installent chez les autres agents avec `scripts/install.py`.

## Règles de structure

- Un skill = un dossier `plugins/<plugin>/skills/<nom>/` contenant `SKILL.md` (+ `references/` et `scripts/` optionnels).
- Frontmatter obligatoire : `name` (= nom du dossier, kebab-case, ≤ 64 caractères) et `description` (≤ 1024 caractères, dit **quand** utiliser le skill, mots-clés FR + EN).
- `SKILL.md` < 300 lignes. Les détails vont dans `references/*.md`, cités par chemin relatif depuis `SKILL.md`.
- Un skill ne référence **jamais** un fichier hors de son plugin : seul le dossier du plugin est copié à l'installation.
- Pas de doublon de contenu entre skills : renvoyer vers le skill qui fait foi (ex. « appliquer `powerbi-conventions` »).
- Un sous-agent = un fichier `plugins/<plugin>/agents/<nom>.md` (frontmatter `name` = nom du fichier, `description`). Il désigne les skills à appliquer et ne recopie pas leurs règles.

## Portabilité entre agents

- Dans un skill, écrire « l'agent » : jamais le nom d'un produit, jamais de variable ou de chemin propre à un agent (`validate.py` le signale).
- Un skill ne suppose aucun outil particulier : citer les skills Microsoft ou un serveur MCP comme « s'ils sont installés », et dire quoi faire sinon.
- Les scripts fournis avec un skill sont en Python (bibliothèque standard) et se lancent par leur chemin relatif au dossier du skill.
- Ce qui est propre à un agent vit hors des skills : `commands/` et `agents/` du plugin, `.claude/`, `scripts/install.py`, `docs/agents.md`.

## Documentation

- Tout skill ajouté, renommé ou modifié dans son usage doit être reflété dans `plugins/<plugin>/commands/<plugin>-docs.md` (sections `skills` et `exemples`). `validate.py` refuse un skill absent du guide.
- Un agent pris en charge en plus ou en moins : mettre à jour `scripts/install.py` (table `AGENTS`) et `docs/agents.md`.

## Versionnement

- Toute modification d'un skill ⇒ incrémenter `version` (SemVer) dans `plugins/<plugin>/.claude-plugin/plugin.json`, puis `python scripts/generate_marketplace.py` pour resynchroniser `.claude-plugin/marketplace.json` (sinon le workflow GitHub le fait après le push).
  - correctif / reformulation : patch (1.0.0 → 1.0.1)
  - nouveau skill ou nouvelle règle : mineur (1.0.1 → 1.1.0)
  - règle supprimée ou inversée : majeur (1.1.0 → 2.0.0)
- Ajouter une entrée datée dans `CHANGELOG.md`.
- Lancer `python scripts/validate.py` et `python -m unittest discover -s tests` avant chaque commit.
- Langages du dépôt : **Python** (scripts, bibliothèque standard uniquement, 3.8+) et **Markdown**. Pas de Node, pas de dépendance externe.

## Contenu

- Langue : français ; noms d'objets techniques et code (DAX, TMDL, M, JSON) en anglais ou selon les conventions définies dans `powerbi-conventions`.
- Marquer **« À ADAPTER »** toute valeur par défaut qui n'est pas encore une règle validée par l'équipe.
- Ne jamais inclure d'identifiants de tenant, d'espaces de travail, de jetons ou de données clients.
- Le DAX et le TMDL donnés en exemple doivent être syntaxiquement valides. Un exemple qui n'a pas été exécuté est listé dans la section « À valider » du `CHANGELOG.md`.

## Rôles de maintenance

Quatre fiches de rôle dans `.claude/agents/` — chargées comme sous-agents par Claude Code, lisibles comme simples consignes par tout autre agent :

| Rôle | Fichier | Quand |
|---|---|---|
| Rédaction d'un skill | `.claude/agents/skill-author.md` | écrire un skill à partir d'un cahier des charges |
| Relecture | `.claude/agents/skill-reviewer.md` | avis indépendant avant commit (lecture seule) |
| Vérification du code d'exemple | `.claude/agents/dax-verifier.md` | après ajout ou modification de DAX / TMDL / M |
| Livraison | `.claude/agents/release-manager.md` | version, changelog, guide, marketplace, validation |

L'auteur d'un skill n'est pas son relecteur.
