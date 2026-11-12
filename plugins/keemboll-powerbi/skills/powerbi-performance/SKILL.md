---
name: powerbi-performance
description: "Optimisation des performances Power BI : code DAX (anti-patterns, variables, filtres, itérateurs), taille et cardinalité du modèle (VertiPaq), Power Query (query folding, actualisation incrémentielle), Direct Lake/DirectQuery, rapports lents et méthode de diagnostic (Performance Analyzer, DAX Studio, Best Practice Analyzer). À utiliser pour auditer ou accélérer un modèle, une mesure ou une page de rapport lente, ou pour relire du DAX/M avant mise en production. Triggers: performance, optimisation, optimize, lent, slow, rapide, VertiPaq, cardinalité, taille du modèle, query folding, actualisation, refresh, DAX Studio, Performance Analyzer, best practice."
---

# Performance — DAX, modèle, rapports

Appliquer aussi `powerbi-conventions`. Les corrections de structure renvoient à `powerbi-data-modeling` ; l'écriture TMDL à `powerbi-tmdl`.

## Méthode de diagnostic (toujours mesurer avant d'optimiser)

1. **Localiser** : quelle page / quel visuel est lent ? (Power BI Desktop → *Analyseur de performances*, relever la durée *Requête DAX* vs *Affichage visuel*.)
2. **Isoler** la requête DAX du visuel (copier depuis l'Analyseur) et l'exécuter dans DAX Studio avec *Server Timings* : temps **Formula Engine** (FE) vs **Storage Engine** (SE), nombre de requêtes SE.
   - FE dominant → DAX à réécrire (itérations, contexte).
   - SE dominant / beaucoup de requêtes → modèle (cardinalité, relations) ou filtres.
3. **Taille du modèle** : DAX Studio → *View Metrics* (VertiPaq Analyzer) : colonnes les plus lourdes, cardinalités, taille des relations.
4. **Règles automatiques** : Tabular Editor → *Best Practice Analyzer*.
5. **Corriger un point à la fois** et re-mesurer ; consigner avant / après dans un tableau.

Ne jamais présenter une optimisation comme acquise sans mesure avant/après.

## DAX — règles prioritaires

| Éviter | Préférer | Pourquoi |
|---|---|---|
| `CALCULATE ( [M], FILTER ( Fact, Fact[Col] = "x" ) )` | `CALCULATE ( [M], Fact[Col] = "x" )` | Filtre de colonne poussé au SE, pas d'itération de la table |
| Même sous-expression répétée | `VAR` | Évaluée une seule fois |
| `IFERROR ( a / b, 0 )` | `DIVIDE ( a, b )` | Pas de gestion d'erreur coûteuse |
| `SUMX ( Fact, Fact[Q] * RELATED ( Dim[Prix] ) )` sur des centaines de millions de lignes | Colonne calculée en amont (source / Power Query) | Itération + RELATED par ligne |
| Itérateurs imbriqués (`SUMX` dans `SUMX`) sur grandes tables | Agréger d'abord au bon grain (`SUMMARIZE`/`VALUES` + `SUMX`) | Réduit le nombre de lignes itérées |
| `COUNTROWS ( FILTER ( … ) ) > 0` | `NOT ISEMPTY ( CALCULATETABLE ( … ) )` | Arrêt au premier résultat |
| `ALL ( Fact )` | `REMOVEFILTERS ( Dim[Col] )` ou `ALL` sur colonnes ciblées | Moins de données matérialisées |
| `FORMAT` / concaténations dans les mesures numériques | Chaînes de format (dynamiques si besoin) | Texte = pas de cache, tri cassé |
| `IF` qui renvoie 0 au lieu de BLANK | Laisser `BLANK()` | Les 0 densifient les visuels (toutes les combinaisons) |
| Mesures de comptage `DISTINCTCOUNT` sur colonne à très forte cardinalité | Pré-agréger ou approximer (`APPROXIMATEDISTINCTCOUNT` en DirectQuery) | Coût mémoire / CPU |

Exemples avant/après détaillés : [references/dax-anti-patterns.md](references/dax-anti-patterns.md).

## Modèle — règles prioritaires

- **Supprimer** colonnes et lignes inutiles (historique hors périmètre, colonnes techniques non utilisées).
- **Réduire la cardinalité** : séparer date et heure, arrondir les décimales, retirer les secondes, remplacer GUID/texte long par des clés entières.
- **Types** : entiers pour les clés, `decimal` (fixe) plutôt que `double` pour les montants.
- **Désactiver** Date/heure automatique (crée une table cachée par colonne date).
- **Relations** : 1→\*, unidirectionnelles, sur colonnes entières ; éviter bidirectionnel et `*:*`.
- **Colonnes calculées** → déplacer en Power Query ou à la source.
- **Hautes cardinalités sur les faits** (n° de ligne, horodatage) : ne pas charger si non utilisées.

Détails et seuils : [references/power-query-template.md](references/power-query-template.md).

## Power Query

- Vérifier le **query folding** (clic droit sur l'étape → *Afficher la requête native*) ; placer les étapes non pliables le plus tard possible.
- Filtrer et supprimer les colonnes **en premier**.
- **Actualisation incrémentielle** sur les grosses tables de faits (paramètres `RangeStart` / `RangeEnd`).
- Pas de fusions entre sources différentes si évitable (empêche le folding).

## Rapports

- Au plus 8 visuels par page (heuristique maison, pas une règle Microsoft) ; regrouper les KPI dans un seul visuel carte multi-lignes quand c'est possible.
- Limiter les segments synchronisés et les interactions inutiles (*Modifier les interactions*).
- Éviter les tables/matrices avec des dizaines de milliers de lignes visibles.
- Infobulles de rapport : légères (elles exécutent leurs propres requêtes).
- Visuels personnalisés : vérifier leur coût dans l'Analyseur de performances.
- Option *Réduction des requêtes* (bouton Appliquer sur les segments) pour les modèles DirectQuery.

## Livrable d'audit

| # | Objet | Constat | Mesure avant | Correction | Mesure après | Gain |
|---|---|---|---|---|---|---|
