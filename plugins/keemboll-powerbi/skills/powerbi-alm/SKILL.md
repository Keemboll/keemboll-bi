---
name: powerbi-alm
description: "Cycle de vie (ALM) d'un projet Power BI au format PBIP : structure du dépôt, .gitignore, stratégie de branches et format des commits, travail à plusieurs et conflits TMDL / PBIR, environnements dev / test / prod, paramètres de source, choix entre pipelines de déploiement Fabric et intégration Git, portes de qualité avant fusion et avant mise en production, intégration continue (lean.py sur chaque PR), versions et retour arrière. À utiliser pour organiser un dépôt de projet BI, préparer une demande de fusion ou une mise en production, mettre en place une CI, ou décider comment promouvoir un modèle ou un rapport d'un environnement à l'autre. La mécanique (API Fabric) relève des skills Microsoft. Triggers: ALM, cycle de vie, lifecycle, Git, branche, branch, commit, pull request, PR, merge, conflit, CI/CD, intégration continue, pipeline de déploiement, deployment pipeline, environnement, dev test prod, mise en production, release, livraison, tag, version, rollback, retour arrière, gitignore, PBIP."
---

# powerbi-alm — cycle de vie d'un projet Power BI

Ce skill fixe les **règles maison** : où sont les fichiers, comment on branche, ce qui doit être vrai avant de fusionner et avant de publier. La **mécanique** (API Fabric, pipelines de déploiement, intégration Git de l'espace de travail, publication) relève des skills Microsoft s'ils sont installés — `deployment-pipelines-authoring-cli`, `git-integration-operations-cli`, `powerbi-report-cli`, `semantic-model-authoring` — sinon du portail Fabric, par l'utilisateur.

Applique `powerbi-conventions` (validation avant modification, commit de sauvegarde, confidentialité) : ces règles ne sont pas répétées ici.

## Règles pour l'agent

1. **Lecture seule sur la production.** Jamais d'écriture dans un espace de travail de production, ni de modification d'un modèle publié.
2. **Aucune publication, aucun déploiement, aucune synchronisation d'espace de travail** sans demande explicite de l'utilisateur pour cette action précise.
3. **Jamais de `git push` automatique, jamais de force-push, jamais de réécriture d'historique** (`rebase` d'une branche partagée, `reset --hard`, `commit --amend` d'un commit déjà poussé). L'agent prépare les commits ; l'utilisateur pousse.
4. **Dépôts privés uniquement.** Aucun identifiant de tenant, d'espace de travail ou d'élément, aucune chaîne de connexion, aucun jeton dans le dépôt, les messages de commit ou la CI.
5. Avant toute écriture : arbre Git propre et commit de sauvegarde (`powerbi-conventions`).

## Structure du dépôt

Un dépôt (ou un dossier de premier niveau) **par produit BI** — un modèle sémantique et ses rapports. **À ADAPTER** si l'équipe préfère un dépôt unique multi-projets.

```
<projet>/
├── <Nom>.pbip
├── <Nom>.SemanticModel/      # TMDL — voir powerbi-tmdl
├── <Nom>.Report/             # PBIR
├── SCOPE.md  KPI.md        # besoin et indicateurs — powerbi-project
├── DEBT.md  CHANGES.md  # registre et journal — powerbi-lean
├── DATA_DICTIONARY.md  REPORT.md  RELEASE_NOTES.md  # documentation — powerbi-documentation
├── SECURITY_MODEL.md               # rôles, sensibilité — powerbi-governance
├── tests/                    # requêtes de contrôle, recette — powerbi-testing
├── AGENTS.md                 # consignes pour les agents sur ce projet
└── .gitignore
```

- Enregistrer en **PBIP** avec le modèle en **TMDL** et le rapport en **PBIR** : un `.pbix` ne se relit pas en diff et ne se versionne pas.
- `.gitignore` type et explications : [references/gitignore-pbip.md](references/gitignore-pbip.md). À vérifier **avant le premier commit** : `cache.abf` contient les données chargées.
- Chaque fichier racine a un skill qui fait foi ; ne pas en dupliquer le contenu ailleurs.

## Branches et commits — À ADAPTER

| Branche | Rôle |
|---|---|
| `main` | Ce qui est **relu et prêt à être promu** ; l'espace de dev y est synchronisé. La production correspond au dernier tag `vX.Y.Z`. Protégée : pas de commit direct, fusion par demande de fusion (PR). |
| `feature/<sujet>` | Une évolution (nouvelle page, nouveau lot de mesures). |
| `fix/<sujet>` | Une correction. |

- **Une branche = un changement cohérent**, relisible en une fois. Ne pas mélanger un renommage et une nouvelle page.
- Branches courtes : se remettre à jour depuis `main` souvent, surtout sur le rapport (voir conflits).
- **PR avec revue humaine** obligatoire ; l'agent peut préparer la description (objets touchés, impact sur les visuels, vérifications faites), pas approuver.
- Commits au format conventionnel : `feat(modele): …`, `fix(rapport): …`, `docs: …`, `chore: …`. Une modification journalisée dans `CHANGES.md` utilise le format de `powerbi-lean` : `M-xxx: <résumé>`, un seul commit pour le changement et le journal.
- Un commit ne contient pas à la fois une modification voulue et le bruit d'un simple enregistrement Desktop : relire `git diff` et écarter ce qui n'est pas intentionnel.

## Travail à plusieurs

- TMDL et PBIR découpent le projet en **nombreux petits fichiers** (une table par fichier, un visuel par dossier) : deux personnes qui touchent des objets différents ne se gênent pas. Répartir le travail **par table** et **par page**.
- **Conflit TMDL** (mesure, colonne) : se résout à la main comme du code, en gardant l'indentation ; revalider ensuite (`powerbi-tmdl`).
- **Conflit dans le JSON d'un visuel ou d'une page** : **ne jamais le résoudre à l'aveugle**. Choisir une version entière du fichier (la leur ou la nôtre), puis refaire l'autre changement dans Desktop.
- **`lineageTag`** : identifiant propre à chaque objet. Ne jamais le copier d'un objet à l'autre ni le régénérer sur un objet existant ; en cas de conflit, garder celui de `main`.
- Fichiers à risque (ordre des pages, `model.tmdl`, `relationships.tmdl`, thème) : une seule personne à la fois, annoncée à l'équipe.
- Après fusion : ouvrir le `.pbip` dans Desktop et vérifier qu'il se charge avant de pousser. Synchronisation avec Desktop : `powerbi-tmdl`.

## Environnements — À ADAPTER

| Environnement | Espace de travail | Qui écrit | Données |
|---|---|---|---|
| Dev | un par projet (ou par développeur) | développeurs, agent sur demande | échantillon ou anonymisées |
| Test / recette | un par projet | promotion uniquement | proches de la production |
| Prod | un par projet | promotion uniquement | réelles |

- Rien de propre à un environnement **en dur** dans le modèle : serveur, base, chemin passent par des **paramètres Power Query**, dont la valeur change à la promotion (règles de déploiement ou paramétrage de l'espace cible).
- Les valeurs réelles de ces paramètres et les identifiants d'espaces **ne sont pas dans le dépôt** ; `SECURITY_MODEL.md` décrit qui a accès à quoi (`powerbi-governance`).
- Sécurité, étiquettes et endossement par environnement : `powerbi-governance`.
- Actualisation : planifiée dans l'espace cible selon la fraîcheur fixée dans `SCOPE.md` (`powerbi-project`) ; un échec d'actualisation en production se traite avant toute nouvelle livraison.

### Deux voies de promotion

| | Pipelines de déploiement Fabric | Intégration Git + branches |
|---|---|---|
| Principe | Copie le contenu d'une étape (espace) vers la suivante | Chaque espace est synchronisé avec une branche ; promouvoir = fusionner |
| Convient si | équipe petite, promotion à la main depuis le portail, peu d'automatisation | revue par PR à chaque étape, CI, plusieurs développeurs |
| Source de vérité | l'espace de dev (Git en amont pour le dev seulement) | le dépôt |
| Point d'attention | ce qui est déployé peut diverger du dépôt si on modifie dans le portail | une branche par environnement à maintenir ; paramétrage par environnement à prévoir |

- Les deux se combinent couramment : **Git pour le dev**, pipeline pour test → prod. C'est le choix par défaut — **À ADAPTER**.
- Quelle que soit la voie : **aucune modification directe en test ou en prod** ; tout repart du dev.
- Les éléments pris en charge, les règles de déploiement disponibles et les limites de l'intégration Git **évoluent** : vérifier la documentation Microsoft avant de s'engager, ne pas l'affirmer de mémoire.

## Portes de qualité

| Avant de fusionner dans `main` | Avant la mise en production |
|---|---|
| Revue `powerbi-lean` (mode `review`) : verdict *prêt à commit* | Audit `powerbi-lean` complet sans constat bloquant |
| Tests du changement passés (`powerbi-testing`) | Recette signée (`powerbi-testing`) |
| `CHANGES.md` à jour | Sécurité et étiquette vérifiées (`powerbi-governance`) |
| CI verte | Documentation régénérée (`powerbi-documentation`) |
| Revue humaine approuvée | Performance vérifiée (`powerbi-performance`) |
| | Plan de retour arrière écrit |

Liste détaillée à cocher : [references/release-checklist.md](references/release-checklist.md). L'agent **rapporte** l'état de chaque porte ; il ne déclare pas une porte franchie sans l'avoir vérifiée, et dit ce qu'il n'a pas pu vérifier.

## Intégration continue

Sur chaque PR, exécuter `lean.py audit` et `lean.py dette` (script du skill `powerbi-lean`, lecture seule, bibliothèque standard). Le script **renvoie 0 même s'il y a des constats** : c'est une étape de la CI qui lit la sortie `--json` et décide d'échouer. Exemples GitHub Actions et Azure DevOps, seuils et mise à disposition du script : [references/ci-examples.md](references/ci-examples.md).

- Seuil par défaut — **À ADAPTER** : échec sur un constat de **priorité 1** ou une **incohérence** entre `DEBT.md` et `CHANGES.md` ; le reste est affiché, pas bloquant.
- La CI ne se connecte **à aucun espace de travail** et ne lit aucune donnée : elle analyse les fichiers du dépôt.
- Complément optionnel : Best Practice Analyzer (Tabular Editor) pour les règles de modèle que `lean.py` ne couvre pas.

## Versions et livraison — À ADAPTER

- Une mise en production = un **tag Git annoté** `vX.Y.Z` sur le commit de `main` publié. Majeur : rupture pour les utilisateurs ou les rapports connectés (mesure renommée ou supprimée, changement de grain) ; mineur : nouvelle page, nouvelles mesures ; correctif : le reste.
- Note de version : `powerbi-documentation`. Elle reprend les entrées `M-xxx` depuis le tag précédent.
- **Retour arrière** : republier le contenu du tag précédent (extraire le tag dans une branche `fix/retour-vX.Y.Z`, puis promotion normale). Ne jamais réécrire `main`. Un retour arrière du modèle ne restaure pas les données : prévoir une actualisation.
- Le plan de retour arrière est écrit **avant** la mise en production, dans la PR.

## Processus — préparer une livraison

1. `git status` propre ; branche à jour depuis `main`.
2. Parcourir les portes de qualité ; lancer `lean.py audit` et `lean.py dette`.
3. Rendre un tableau porte / état / preuve / reste à faire, et la description de PR.
4. **S'arrêter** : fusion, tag, push et promotion sont faits par l'utilisateur, ou par l'agent sur demande explicite, une action à la fois.

## Références

- [references/gitignore-pbip.md](references/gitignore-pbip.md) — `.gitignore` type et ce qu'il ne faut jamais versionner.
- [references/release-checklist.md](references/release-checklist.md) — portes de qualité détaillées et plan de retour arrière.
- [references/ci-examples.md](references/ci-examples.md) — workflows GitHub Actions et Azure DevOps, codes de sortie de `lean.py`.
