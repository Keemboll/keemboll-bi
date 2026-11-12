---
name: powerbi-documentation
description: "Documentation d'un projet Power BI : dictionnaire de données généré depuis le modèle (DATA_DICTIONARY.md), catalogue de mesures, fiche de rapport (pages, public, question de chaque page, filtres, limites connues), note de version tirée du journal des modifications et dossier de passation. À utiliser pour documenter un modèle sémantique ou un rapport, préparer une publication, une recette ou une passation, compléter les descriptions manquantes ou expliquer un modèle à un nouvel arrivant. Triggers: documentation, documenter, dictionnaire de données, data dictionary, catalogue de mesures, measure catalog, fiche de rapport, note de version, release notes, passation, handover, onboarding, description manquante, glossaire, lineage."
---

# powerbi-documentation — documenter sans réécrire le modèle

But : toute personne qui reprend le projet comprend **ce que mesure chaque indicateur, d'où il vient et à quoi sert chaque page**, sans ouvrir Power BI Desktop. La documentation est **générée** depuis le modèle partout où c'est possible, et **rédigée** seulement pour ce que le modèle ne sait pas (le pourquoi métier, le public, les limites).

Applique `powerbi-conventions` (descriptions obligatoires, confidentialité des métadonnées, validation avant modification) et `powerbi-tmdl` (écriture des descriptions `///`). **Lecture seule par défaut** : ce skill n'écrit que des fichiers Markdown de documentation, après accord.

## Les livrables

À la racine du projet, à côté du `.pbip`, versionnés avec lui (dossier `docs/` possible — **À ADAPTER**) :

| Fichier | Contenu | Origine |
|---|---|---|
| `DATA_DICTIONARY.md` | Tables, colonnes, mesures et leur DAX, relations, rôles, objets sans description | **Généré** par `lean.py catalogue` |
| `REPORT.md` | Fiche du rapport : public, question de chaque page, filtres, limites connues | Rédigé — [report-sheet-template.md](references/report-sheet-template.md) |
| `RELEASE_NOTES.md` | Ce qui change pour les utilisateurs à chaque publication | Tiré de `CHANGES.md` — [release-notes-template.md](references/release-notes-template.md) |
| `HANDOVER.md` | Ce qu'il faut savoir pour reprendre le projet | Rédigé — [handover-template.md](references/handover-template.md) |

Le **catalogue de mesures** n'est pas un fichier à part : ce sont les sections « Mesures » de `DATA_DICTIONARY.md`, classées par table et dossier d'affichage. Pour un public métier, en extraire un tableau *mesure / définition / format* sans le DAX.

Ne pas dupliquer ce que d'autres fichiers portent déjà : besoin et indicateurs (`SCOPE.md`, `KPI.md` — skill `powerbi-project`), sécurité (`SECURITY_MODEL.md` — `powerbi-governance`), tests et recette (`tests/`, `tests/ACCEPTANCE.md` — `powerbi-testing`), branches et déploiement (`powerbi-alm`), dette et journal (`DEBT.md`, `CHANGES.md` — `powerbi-lean`). La documentation **renvoie** vers eux.

## Générer le dictionnaire

Le script est celui du skill voisin `powerbi-lean` (même plugin), en lecture seule ; il écrit sur la sortie standard :

```bash
python "<dossier du skill powerbi-lean>/scripts/lean.py" catalogue "<dossier du projet>"          # Markdown
python "<dossier du skill powerbi-lean>/scripts/lean.py" catalogue "<dossier du projet>" --json   # sortie exploitable
```

Sous Windows `python` (ou `py`), ailleurs `python3`. Rediriger la sortie vers `DATA_DICTIONARY.md` en UTF-8 (sous Windows PowerShell 5.1, `>` écrit en UTF-16 : utiliser `| Out-File -Encoding utf8 DATA_DICTIONARY.md`), ou la relire puis l'écrire avec l'outil d'écriture de fichiers.

Le dictionnaire contient : compteurs, liste des tables (type déduit du préfixe, masquée ou non), colonnes (type, description, masquée, agrégation, colonne de tri, format), mesures (description, format, masquée, utilisée par le rapport, DAX), relations (cardinalité, filtrage croisé, active), rôles RLS et la section **« Sans description »**. Le filtre d'un rôle qui contient une adresse e-mail n'est pas recopié.

## Processus

1. **Générer** `DATA_DICTIONARY.md` avec `lean.py catalogue`. Ne jamais le rédiger à la main ni à partir de suppositions.
2. **Lire la section « Sans description »** et la présenter à l'utilisateur. Pour chaque objet : demander la définition métier, ou proposer une formulation **marquée comme proposition** à valider. Ne jamais inventer une définition.
3. **Corriger dans le modèle** : les descriptions validées s'écrivent en `///` dans les fichiers TMDL (`powerbi-tmdl`), selon le processus de validation de `powerbi-conventions`. Jamais dans `DATA_DICTIONARY.md`.
4. **Régénérer** le dictionnaire ; la section « Sans description » doit avoir diminué.
5. **Rédiger ou mettre à jour** `REPORT.md` à partir des pages réelles du rapport (`lean.py usage` donne les champs par page et par visuel) et des réponses de l'utilisateur sur le public et les questions.
6. **Avant publication** : note de version depuis les entrées `M-xxx` ajoutées depuis la dernière publication.
7. Un seul commit pour le changement de modèle et la documentation régénérée.

## Quand régénérer

- Avant chaque publication (voir `powerbi-alm`).
- Après chaque modification `M-xxx` qui touche le modèle : mesure, colonne, relation, rôle, description.
- Avant une recette ou une passation.

Un dictionnaire plus ancien que le dernier commit du modèle est faux : le dire plutôt que de s'en servir.

## Règles

- **Source de vérité = le modèle.** Une description fausse se corrige dans le TMDL, puis on régénère. Toute correction faite directement dans `DATA_DICTIONARY.md` sera perdue.
- **Documenter le pourquoi, pas paraphraser le DAX.** « Clients ayant commandé au moins une fois sur la période, hors comptes internes » — pas « DISTINCTCOUNT de CustomerKey ». Le DAX figure déjà dans le dictionnaire.
- Une description de mesure dit : **définition métier, règle de calcul, périmètre, source**. Une description de colonne dit ce que contient la valeur et son unité.
- **Aucune valeur réelle** (montants, noms de clients, de patients, d'agents) ni donnée personnelle dans la documentation : exemples fictifs uniquement. Si le script signale un filtre masqué, ne pas aller le recopier.
- **Signaler** ce qui manque (description, format, propriétaire d'un indicateur) plutôt que combler par une supposition.
- « Utilisée par le rapport : non » = non référencée par **ce** rapport ; un autre rapport connecté au modèle publié peut l'utiliser (voir `powerbi-lean`).
- Vocabulaire : reprendre les libellés du modèle et de `KPI.md` à l'identique ; un même indicateur n'a qu'un nom.
- Pas de capture d'écran contenant des données réelles ; préférer la maquette (`powerbi-mockup`) pour illustrer une page.

## Références

- [references/report-sheet-template.md](references/report-sheet-template.md) — fiche d'un rapport, page par page.
- [references/release-notes-template.md](references/release-notes-template.md) — note de version pour les utilisateurs.
- [references/handover-template.md](references/handover-template.md) — dossier de passation.
