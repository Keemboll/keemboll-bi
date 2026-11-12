# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) — versionnement [SemVer](https://semver.org/lang/fr/).

## [1.6.0] — 2026-11-11

Le plugin passe de « règles pour construire un modèle et un rapport » à la gestion d'un projet BI de bout en bout, et s'ouvre aux agents autres que Claude Code.

### Ajouté
- Skill **`powerbi-project`** : phases d'un projet BI (cadrage → exploitation), livrable et critère de sortie de chaque phase, skill qui fait foi, fiche de cadrage `SCOPE.md`, catalogue de KPI `KPI.md`, rôles, definition of done.
- Skill **`powerbi-governance`** : RLS statique et dynamique, OLS, étiquettes de sensibilité, endossement, rôles d'espace de travail, partage, données personnelles, fiche `SECURITY_MODEL.md`.
- Skill **`powerbi-testing`** : six niveaux de test (intégrité, rapprochement, mesures, non-régression, RLS, rapport), requêtes DAX de contrôle, dossier `tests/` et procès-verbal `tests/ACCEPTANCE.md`.
- Skill **`powerbi-alm`** : dépôt PBIP, `.gitignore`, branches et commits, environnements, choix pipelines de déploiement / intégration Git, portes de qualité, exemples de CI (GitHub Actions, Azure DevOps), versions et retour arrière.
- Skill **`powerbi-documentation`** : dictionnaire de données généré, fiche de rapport, note de version, dossier de passation.
- `lean.py catalogue` : dictionnaire de données en Markdown (ou `--json`) sur la sortie standard, à partir du TMDL et du rapport ; un filtre RLS qui contient une adresse e-mail n'est pas recopié.
- Sous-agents du plugin (`plugins/keemboll-powerbi/agents/`) : `powerbi-auditor` (lecture seule), `powerbi-modeler`, `powerbi-report-designer`.
- **Ouverture aux autres agents** : `scripts/install.py` installe les skills dans un projet BI pour Codex, Grok, Gemini, Copilot, Cursor ou tout agent qui lit `AGENTS.md` (copie des skills, bloc d'index dans `AGENTS.md`, mise à jour et désinstallation propres) ; `scripts/build_dist.py` produit un `.zip` par skill, un `.zip` d'ensemble et tous les skills en un seul fichier Markdown ; guide `docs/agents.md`.
- `AGENTS.md` devient la source des règles du dépôt pour tous les agents (section « Portabilité entre agents ») ; `CLAUDE.md` l'importe.
- Rôles de maintenance du dépôt dans `.claude/agents/` : `skill-author`, `skill-reviewer`, `dax-verifier`, `release-manager`.
- `validate.py` : contrôle des sous-agents, des liens relatifs de tous les fichiers Markdown d'un skill (cassés ou hors du plugin), des skills cités qui n'existent pas ; avertissement si un `SKILL.md` nomme un agent précis.
- Tests (`tests/`, `python -m unittest discover -s tests`) des scripts du dépôt et de `lean.py` sur un projet PBIP d'exemple ; workflow `validate.yml` sur chaque demande de fusion et chaque branche.
- `/keemboll-docs` : sections `projet` et `agents`, 14 skills, nouveaux exemples de demandes.

### Modifié
- `powerbi-conventions` : la section « Sécurité et gouvernance » renvoie à `powerbi-governance` pour la conception des rôles.
- `powerbi-report-design` (`svg-backgrounds.md`) : formulation indépendante de l'agent.
- `README.md` : contenu par étape du projet, installation pour les autres agents.

### À valider
Aucun moteur DAX n'était disponible : rien de ce qui suit n'a été exécuté.
- Requêtes DAX de contrôle de `powerbi-testing` (`check-queries.md`).
- Exemples TMDL et DAX de rôles RLS / OLS de `powerbi-governance` (`rls-ols.md`).
- Workflows GitHub Actions et Azure DevOps de `powerbi-alm` (`ci-examples.md`) : YAML relus, jamais lancés.
- Emplacements des skills par agent (`docs/agents.md`) : relevés dans la documentation des éditeurs, non testés avec chaque agent ; celui de Cursor au niveau du projet n'est pas confirmé.
- `lean.py catalogue` : testé sur le projet d'exemple `tests/fixture/Demo` seulement.

## [1.5.1] — 2026-10-27

### Corrigé
- `powerbi-tmdl`, `powerbi-report-design`, `/keemboll-docs` : le **rechargement des changements externes** (préversion, Desktop d'août 2026 ou plus récent, option *Detect and reload external PBIP changes*) et le **Desktop Bridge** (Options → Sécurité, activé par défaut ; la doc le signale aussi comme préversion) sont désormais deux mécanismes distincts.
- `powerbi-data-modeling`, `powerbi-performance` : **Direct Lake on OneLake** (recommandé pour les nouveaux modèles ; pas de repli DirectQuery, composite possible, colonnes calculées en contexte utilisateur en préversion, garde-fous dépassés = requête en erreur) distingué de **Direct Lake on SQL analytics endpoint** (repli DirectQuery, `DirectLakeBehavior`).
- `powerbi-performance` : `SWITCH` s'arrête à la première valeur qui correspond ; le conseil paramètre de champs / groupe de calcul relève de l'ergonomie, pas de la performance.
- Nombre de visuels par page aligné : 6 à 8 (`powerbi-report-design`) et au plus 8 (`powerbi-performance`), présenté comme heuristique maison.
- `powerbi-dax-library` : moyenne mobile 3 mois (`CALCULATE` autour d'`AVERAGEX`, comportement des mois vides documenté) ; `_dateMax` remplacé par `_Date max ventes` ; Nouveaux clients / Clients perdus via `SUMMARIZE` sur `CustomerCode` (SCD2) ; Part dans la catégorie sur tous les niveaux sous la catégorie ; ajout de `CA HT YTD fiscal`.
- `powerbi-performance` (anti-patterns §2 et §6) : `CustomerCode` au lieu de `CustomerKey`, avec note SCD2.
- `powerbi-data-modeling` (`dim-date.md`) : bornes de la table de dates calculées sur `DateCommande` et `DateLivraison`.

### À valider
Aucun moteur DAX n'était disponible (ni Tabular Editor CLI, ni DAX Studio, ni serveur MCP de modélisation) : ces mesures n'ont **pas** été exécutées.
- `CA HT moyenne mobile 3 mois` (`time-intelligence.md`)
- `CA HT YTD fiscal` (`time-intelligence.md`)
- `Nouveaux clients`, `Clients perdus` (`ratios-rankings.md`)
- `Part dans la catégorie %` (`ratios-rankings.md`)
- `CA gros clients` et `Moyenne CA par client` (`dax-anti-patterns.md`)
- `Dim_Date` en DAX avec `DateLivraison` (`dim-date.md`)

## [1.5.0] — 2026-10-16

### Ajouté
- Commande **`/keemboll-docs [section]`** : guide d'utilisation du plugin (installation, skills, exemples de demandes, `lean.py`, dette et journal, méthode, sécurité, dépannage) pour tout nouvel utilisateur.
- `validate.py` : vérifie que chaque skill est présenté dans la commande de documentation et que chaque commande a un frontmatter.

## [1.4.1] — 2026-10-16

### Ajouté
- `powerbi-lean` : procédure d'initialisation de `CHANGES.md` sur un projet qui a déjà une dette (reprise de l'historique Git, sans invention).
- Référence `D-xxx (partielle)` / `(en cours)` dans le journal : avancée qui ne solde pas la dette, acceptée par `lean.py dette`.

## [1.4.0] — 2026-10-15

### Ajouté
- `powerbi-lean` : journal **`CHANGES.md`** (modèle `changes-template.md`) qui se remplit à mesure que la dette diminue ; procédure « solder une dette » (entrée M-xxx, déplacement de D-xxx dans « Soldé », commit `M-xxx: …`).
- `lean.py dette` : état de la dette (ouvertes / soldées, progression, priorités, échéances dépassées), prochains identifiants D-xxx / M-xxx et contrôle de cohérence entre `DEBT.md` et `CHANGES.md`.

### Modifié
- `debt-template.md` : une dette soldée renvoie à sa modification (`**Modification** : M-xxx`) au lieu d'un hash de commit.

## [1.3.0] — 2026-10-14

### Modifié
- `powerbi-lean` : le script d'audit passe de Node (`lean.mjs`) à **Python** (`lean.py`, 3.8+, bibliothèque standard uniquement). Mêmes commandes (`audit`, `usage`, `--changed`, `--field`, `--json`) et mêmes résultats, vérifiés sur le projet SalesCockpit et sur un jeu de test.
- Sortie console forcée en UTF-8 (compatibilité Windows) ; ordre des résultats déterministe.

- Scripts du dépôt passés en Python (bibliothèque standard) : `validate.py`, `generate_marketplace.py` (même sortie octet pour octet), `bump_versions.py` ; le workflow GitHub Actions utilise `setup-python`. Le dépôt ne contient plus que du Python et du Markdown.

### Supprimé
- `lean.mjs` (remplacé par `lean.py`).
- `scripts/*.mjs` et `package.json` (remplacés par les scripts Python).

## [1.2.0] — 2026-10-13

### Ajouté
- Skill `powerbi-lean` (« moins d'objets, pas moins de documentation ») : modes `review` (git diff), `audit` (projet complet) et `dette` (registre `DEBT.md` hors modèle). Alternative maison à ponytail, sans hook ni activation permanente.
- Script `powerbi-lean/scripts/lean.mjs` (Node, sans dépendance, lecture seule) : audit TMDL + PBIR (inutilisés, doublons, valeurs en dur, FILTER sur table, summarizeBy, clés visibles, table de dates), option `--changed`, et `usage` pour l'inventaire des champs utilisés avant un renommage. Testé sur le projet d'exemple SalesCockpit.

## [1.1.0] — 2026-10-13

Inspiré du guide « How I Build Power BI Reports with AI » (L. Reese).

### Ajouté
- Skill `powerbi-mockup` : maquette HTML d'une page à partir du modèle réel (champs étiquetés, mesures manquantes listées, itérations, passage au PBIP) avec gabarit et checklist.
- `powerbi-report-design` : quatre questions par page, jetons de design chiffrés, structure en Z avec interrupteurs, vérification visuelle par capture, revue « 5 problèmes », fonds de page SVG (`svg-backgrounds.md`), boucle de références visuelles (`references/visuals/`, modèle d'entrée et première référence « carte KPI avec comparaison »).
- `powerbi-dax-library` : interrupteurs par tables déconnectées (Plan / N-1, Haut / Bas, Mensuel / Cumul), titres et couleurs dynamiques.
- `powerbi-conventions` : règles « modèle existant vs nouveau modèle », confidentialité des métadonnées (données de santé / personnelles), commentaire QUOI / COMMENT / ADAPTER dans les mesures, Git obligatoire avant écriture.

### Modifié
- `powerbi-conventions` : précision `DIVIDE(a, b, 0)` ≠ `COALESCE(DIVIDE(a, b), 0)`.
- `powerbi-tmdl` : synchronisation avec Desktop (enregistrer avant, appliquer les changements externes ou Desktop Bridge) au lieu de « fermer Desktop ».

## [Non publié] — 2026-10-13

### Ajouté
- `scripts/bump-versions.mjs` : incrémente automatiquement la version d'un plugin modifié (niveau déduit des messages de commit).
- `scripts/generate-marketplace.mjs` (`npm run generate`, option `--check`) : génère la liste `plugins` de `marketplace.json` depuis les `plugin.json`.
- Workflow GitHub Actions `generate-marketplace.yml` (webhook `push` sur `main`) : régénère et commit `marketplace.json` automatiquement.

## [1.0.0] — 2026-10-13

### Ajouté
- Marketplace `keemboll` et plugin `keemboll-powerbi`.
- Skills : `powerbi-conventions`, `powerbi-data-modeling`, `powerbi-tmdl`, `powerbi-dax-library`, `powerbi-performance`, `powerbi-report-design`, `powerbi-html-visuals`.
- Modèle de skill (`templates/skill-template/`) et script `scripts/validate.mjs`.
