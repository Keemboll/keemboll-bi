# Intégration continue — exemples

La CI analyse **les fichiers du dépôt** avec `lean.py` (skill `powerbi-lean`). Elle ne se connecte à aucun espace de travail, ne lit aucune donnée et n'a besoin d'aucun secret.

## Ce que renvoie `lean.py`

| Commande | Code de sortie | Sortie |
|---|---|---|
| `audit <projet> [--json]` | **0**, qu'il y ait des constats ou non | `--json` : `{"findings": [{"prio", "cat", "obj", "detail", "file"}], "stats": {…}}` — `prio` vaut 1, 2 ou 3 |
| `dette <projet> [--json]` | **0**, qu'il y ait des incohérences ou non | `--json` : `open`, `closed`, `progress`, `openItems`, `issues` (liste de textes) … |
| sous-commande inconnue | **1** | aide sur la sortie standard |
| `audit` : aucun dossier `*.SemanticModel`, dossier absent, erreur de lecture | **1** | message sur la sortie d'erreur |
| `dette` : `DEBT.md` et `CHANGES.md` absents, ou mauvais dossier | **0**, `total: 0`, `issues: []` | la porte passe à vide — vérifier `PROJET` |

Conséquence : **le script ne fait jamais échouer le build à cause d'un constat**. Il n'existe pas d'option de seuil, et une option inconnue est ignorée sans erreur. C'est une étape de la CI qui lit le JSON et décide. Le petit script ci-dessous (`ci_seuil.py`, à placer dans le dépôt du projet, p. ex. dans `tests/`) applique le seuil par défaut — **À ADAPTER** : échec sur un constat de priorité 1 ou une incohérence dette / journal.

```python
"""Seuil de la CI : python ci_seuil.py audit.json dette.json"""
import json
import sys

audit = json.load(open(sys.argv[1], encoding="utf-8"))
dette = json.load(open(sys.argv[2], encoding="utf-8"))
bloquants = [f for f in audit["findings"] if f["prio"] == 1]
for f in bloquants:
    print(f"BLOQUANT {f['cat']} : {f['obj']} - {f['detail']}")
for i in dette["issues"]:
    print(f"INCOHERENCE {i}")
print(f"{len(audit['findings'])} constat(s), dont {len(bloquants)} bloquant(s) ; "
      f"{len(dette['issues'])} incoherence(s) dette / journal.")
sys.exit(1 if bloquants or dette["issues"] else 0)
```

`dette` signale aussi les **échéances dépassées** dans `issues` : avec ce seuil, une dette en retard bloque la PR. Filtrer ces lignes dans `ci_seuil.py` si ce n'est pas voulu.

## Rendre le script disponible

La CI n'a pas accès aux skills installés sur le poste. Le script doit être **dans le dépôt du projet** : les skills installés dans le projet, p. ex. `.agents/skills/powerbi-lean/`, versionnés avec lui. Adapter la variable `LEAN` ci-dessous au dossier réellement utilisé. Mettre à jour cette copie quand le skill évolue.

Dans les exemples, `PROJET` est le dossier qui contient le `.pbip` (`.` s'il est à la racine).

## GitHub Actions

`.github/workflows/powerbi-qualite.yml`

```yaml
name: Qualité Power BI

on:
  pull_request:
    branches: [main]

permissions:
  contents: read

env:
  LEAN: .agents/skills/powerbi-lean/scripts/lean.py
  PROJET: .

jobs:
  lean:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Audit (lisible dans le journal)
        run: python "$LEAN" audit "$PROJET"
      - name: Dette et journal
        run: python "$LEAN" dette "$PROJET"
      - name: Seuil
        run: |
          python "$LEAN" audit "$PROJET" --json > audit.json
          python "$LEAN" dette "$PROJET" --json > dette.json
          python tests/ci_seuil.py audit.json dette.json
```

## Azure DevOps

`azure-pipelines.yml` — pour qu'il s'exécute sur les PR d'un dépôt Azure Repos, ajouter une **stratégie de validation de build** sur la branche `main` (les déclencheurs `pr:` du YAML ne s'appliquent pas à Azure Repos).

```yaml
trigger: none

pool:
  vmImage: ubuntu-latest

variables:
  LEAN: .agents/skills/powerbi-lean/scripts/lean.py
  PROJET: .

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: "3.12"
  - script: python "$(LEAN)" audit "$(PROJET)"
    displayName: Audit (lisible dans le journal)
  - script: python "$(LEAN)" dette "$(PROJET)"
    displayName: Dette et journal
  - script: |
      python "$(LEAN)" audit "$(PROJET)" --json > audit.json
      python "$(LEAN)" dette "$(PROJET)" --json > dette.json
      python tests/ci_seuil.py audit.json dette.json
    displayName: Seuil
```

## Variantes

- **Constats limités à la PR** : `audit --changed` compare l'arbre de travail au dernier commit ; dans une CI, l'arbre est propre, donc l'option ne renvoie rien d'utile. Pour ne bloquer que sur les fichiers de la PR, filtrer dans `ci_seuil.py` les constats dont `file` (chemin **absolu** ; `null` pour un constat de modèle, à garder) correspond, une fois rendu relatif à la racine du dépôt (`os.path.relpath`), à une ligne de `git diff --name-only origin/main...HEAD` (prévoir alors un clone complet, `fetch-depth: 0`).
- **Dictionnaire à jour** : `python "$LEAN" catalogue "$PROJET" > DATA_DICTIONARY.md`, puis `git diff --exit-code -I '^> Généré le ' DATA_DICTIONARY.md` (Git 2.30+ ; `-I` ignore la ligne de date) : le build échoue si le dictionnaire versionné ne correspond plus au modèle (`powerbi-documentation`).
- **Tests** : les requêtes de contrôle de `tests/` demandent un moteur et des données ; elles ne s'exécutent pas dans cette CI sans connexion (`powerbi-testing`).
- **Best Practice Analyzer** (Tabular Editor) : complément optionnel pour les règles de modèle ; à ajouter comme étape séparée selon la version et la licence de l'outil dont dispose l'équipe.
- **Plusieurs projets dans un dépôt** : une exécution par dossier de projet (matrice de jobs).

## Ce que la CI ne remplace pas

La revue humaine, la recette métier, le test des rôles de sécurité et la vérification des valeurs dans Power BI Desktop. Une CI verte signifie « aucun constat bloquant détectable dans les fichiers », pas « prêt pour la production ».
