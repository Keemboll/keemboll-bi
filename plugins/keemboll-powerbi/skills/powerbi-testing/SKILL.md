---
name: powerbi-testing
description: "Tests, qualité des données et recette d'un modèle sémantique ou d'un rapport Power BI : intégrité du modèle (clés uniques, clés vides, intégrité référentielle, table de dates), rapprochement avec la source, tests de mesures DAX, non-régression avant / après un changement, tests des rôles RLS, vérification du rapport, dossier tests/ de requêtes DAX de contrôle et procès-verbal tests/ACCEPTANCE.md. À utiliser pour vérifier un modèle ou une mesure, prouver qu'une modification n'a rien cassé, tester la sécurité, préparer ou conduire une recette avant publication. Triggers: test, tests, tester, vérifier, vérification, contrôle, qualité des données, data quality, rapprochement, reconciliation, non-régression, regression, recette, UAT, validation, EVALUATE, requête DAX, DAX query, écart, valeurs avant après, intégrité référentielle, referential integrity, doublon de clé, tester la RLS."
---

# Tests, qualité des données et recette

But : aucune publication sans **preuve** que les chiffres sont justes, que le changement n'a rien cassé et que chacun ne voit que son périmètre.

Applique `powerbi-conventions` (validation, confidentialité). Renvoie à : `powerbi-governance` (conception des rôles), `powerbi-performance` (lenteur), `powerbi-lean` (`DEBT.md`), `powerbi-alm` (déploiement, intégration continue), `powerbi-project` (phases, `KPI.md`), `powerbi-dax-library` (formules de référence).

## Règles

1. **Ne jamais prétendre avoir vérifié** ce qui n'a pas été exécuté. Sans moteur DAX disponible, fournir les requêtes à lancer par l'utilisateur (DAX Studio, ou vue Requête DAX de Power BI Desktop) et l'écrire clairement : « non exécuté ».
2. Une requête exécutée par l'agent (serveur MCP, point de terminaison XMLA) renvoie de **vraies données** : demander l'accord de l'utilisateur, limiter aux agrégats nécessaires, ne pas recopier les résultats dans des fichiers.
3. **Aucune valeur réelle sensible** dans les fichiers versionnés (`tests/`, `ACCEPTANCE.md`, `DEBT.md`) : on note *conforme / non conforme* et l'ordre de grandeur de l'écart si utile, pas les chiffres.
4. Un test qui échoue ne se « corrige » **pas en changeant l'attendu**. Soit le modèle est faux, soit l'attendu était faux et c'est le métier qui le dit.
5. L'**attendu vient du métier ou de la source** (définition dans `KPI.md`, total du système source), jamais de la mesure qu'on teste.
6. Un écart non résolu et accepté va dans `DEBT.md` avec sa cause supposée ; il n'est pas passé sous silence.
7. **Recette signée par le métier** avant publication en production.
8. Les tests sont en **lecture seule** : une requête de contrôle ne modifie jamais le modèle.

## Les six niveaux

| # | Niveau | Question | Quand |
|---|---|---|---|
| 1 | **Intégrité du modèle** | Clés uniques dans les dimensions ? Clés vides ? Chaque fait trouve-t-il sa dimension ? La table de dates est-elle continue et couvre-t-elle les faits ? | Après tout changement de modèle ou de source ; à chaque actualisation si automatisé |
| 2 | **Rapprochement source** | Les totaux de contrôle par période égalent-ils ceux du système source ? | Nouveau modèle, nouvelle source, changement Power Query |
| 3 | **Mesures** | Cas connus justes ? Total = somme des détails (si additif) ? Bords : période vide, N-1 absent, division par zéro, sélection multiple ? | Toute mesure créée ou modifiée |
| 4 | **Non-régression** | Même requête avant et après : mêmes valeurs ? | Refactorisation, renommage, optimisation, fusion de doublons |
| 5 | **RLS / OLS** | Chaque rôle voit-il exactement son périmètre ? L'utilisateur sans droit ne voit-il rien ? | Tout changement de rôle, de table de sécurité ou de relation |
| 6 | **Rapport** | Filtres, segments, interactions, signets, extraction, infobulles, valeurs affichées = valeurs testées ? Temps de chargement acceptable ? | Avant recette |

Requêtes prêtes à adapter pour chaque niveau : [references/check-queries.md](references/check-queries.md).

Précisions :

- **Niveau 1** — un doublon de clé côté « un » empêche la relation ; un fait orphelin apparaît sous une ligne **vide** dans les visuels et fausse les parts. La ligne vide est le symptôme à chercher.
- **Niveau 2** — rapprocher au **grain le plus fin utile** (mois × société, par exemple) : un total général juste peut cacher deux erreurs qui se compensent. Convenir d'une tolérance d'arrondi — **À ADAPTER** (défaut : 0,01 unité monétaire par ligne de contrôle).
- **Niveau 3** — une mesure non additive (nombre de clients distincts, ratio, moyenne) n'a **pas** à vérifier « total = somme des détails » : tester sa définition, pas l'additivité.
- **Niveau 4** — capturer l'« avant » **avant** de modifier (commit de sauvegarde, résultat conservé hors dépôt), ou définir la nouvelle version dans la requête avec `DEFINE MEASURE` pour comparer les deux côte à côte.
- **Niveau 5** — un test fait dans le service par un Admin, Membre ou Contributeur de l'espace de travail ne prouve rien : la RLS ne s'applique pas à lui. Protocole ci-dessous.
- **Niveau 6** — la lenteur se diagnostique avec `powerbi-performance` ; seuil d'acceptation — **À ADAPTER** (défaut : page affichée en moins de 5 s).

## Protocole de test RLS (par rôle)

1. Lister depuis `SECURITY_MODEL.md` (`powerbi-governance`) : rôle, périmètre attendu, profil de test.
2. Dans Power BI Desktop : Modélisation → **Afficher comme** → cocher le rôle (et « Autre utilisateur » avec un UPN de test pour un rôle dynamique). Dans le service : **Tester en tant que rôle** sur la sécurité du modèle. Attention, rôle dynamique : dans le service, ce test utilise par défaut l'identité de celui qui teste ; choisir une personne dans « Affichage actuel en tant que » ou, à défaut, se connecter avec un compte Lecteur de test. Les libellés varient selon la version.
3. Exécuter la requête de contrôle du rôle : liste des valeurs visibles de la dimension filtrée + total de la mesure principale.
4. Vérifier : (a) périmètre visible = périmètre attendu, ni plus ni moins ; (b) le total = somme des seuls périmètres autorisés ; (c) les pages de détail, l'extraction et l'export respectent le filtre.
5. Cas obligatoires : utilisateur **absent** de la table de sécurité (ne voit rien), lecteur **rattaché à aucun rôle** (aucune donnée — à tester avec un compte Lecteur réel, « Afficher comme » ne le simule pas), utilisateur à **plusieurs périmètres**, utilisateur membre de **deux rôles** RLS (union), rôle « tout voir » s'il existe.
6. OLS : vérifier que l'objet est invisible et noter quels visuels tombent en erreur pour ce rôle.
7. Consigner dans `tests/ACCEPTANCE.md` et reporter la date dans `SECURITY_MODEL.md`.

## Organisation dans le projet

```
<projet>/
├── tests/
│   ├── T-001_integrite_cles.dax
│   ├── T-010_rapprochement_ca_mensuel.dax
│   ├── T-020_ca_ht_n1.dax
│   └── ACCEPTANCE.md
```

- Un fichier `.dax` par test, nommé `T-xxx_<objet>.dax` ; numérotation par dizaines selon le niveau — **À ADAPTER**.
- En-tête obligatoire :

```dax
// QUOI : aucun client en double dans Dim_Client.
// ATTENDU : zéro ligne.
EVALUATE
FILTER (
    SUMMARIZECOLUMNS ( Dim_Client[CustomerKey], "Nb lignes", COUNTROWS ( Dim_Client ) ),
    [Nb lignes] > 1
)
```

- Écrire de préférence des tests qui renvoient **zéro ligne quand tout va bien** : le résultat se lit d'un coup d'œil et s'automatise (`powerbi-alm`).
- `tests/ACCEPTANCE.md` : procès-verbal — cas, attendu, résultat, qui, date, décision. Modèle : [references/acceptance-template.md](references/acceptance-template.md).

## Processus

1. **Cadrer** : quel changement, quels objets touchés (`powerbi-lean`, commande `usage`), quels niveaux de test s'appliquent.
2. **Écrire ou reprendre** les requêtes dans `tests/` ; les montrer avant exécution.
3. **Exécuter** (avec accord) ou **remettre** les requêtes à l'utilisateur ; pour une non-régression, capturer l'« avant » d'abord.
4. **Comparer** à l'attendu ; en cas d'écart, chercher la cause dans l'ordre : filtre de la requête → relation / grain → Power Query → source → définition métier.
5. **Consigner** dans `ACCEPTANCE.md` ; écarts acceptés dans `DEBT.md`.
6. **Restituer** un tableau test / niveau / résultat / exécuté par (agent, utilisateur, non exécuté), puis un verdict : *prêt pour recette métier* / *à corriger*.

## Recette métier

- Qui : le propriétaire métier désigné dans `SCOPE.md` (`powerbi-project`), pas l'auteur du rapport.
- Quoi : les cas de `ACCEPTANCE.md` lisibles par un non-technicien (« le CA de mars pour la région Nord égale celui du rapport de gestion »).
- Décision : *accepté* / *accepté avec réserves* (réserves → `DEBT.md` avec échéance) / *refusé*.
- Sans décision écrite et datée : pas de mise en production.
