# Ce que vérifie `lean.py audit`

| Priorité | Catégorie | Règle |
|---|---|---|
| 1 | Doublon | Mesures dont le DAX est identique une fois commentaires et espaces retirés |
| 1 | Modèle | Aucune table marquée comme table de dates (`dataCategory: Time`) |
| 2 | Inutilisée | Mesure non utilisée par le rapport, ni par une mesure utilisée, ni par un rôle, un groupe de calcul, une table calculée ou une chaîne de format |
| 2 | Inutilisée | Colonne non utilisée (rapport, DAX, relations, colonnes de tri, hiérarchies, clé de la table de dates) — tables de mesures exclues |
| 2 | DAX | `FILTER` appliqué directement à une table du modèle |
| 2 | Valeur en dur | `TODAY()` / `NOW()`, `IFERROR` / `ISERROR` |
| 2 | Modèle | `summarizeBy: sum` sur une colonne au nom d'identifiant, de code ou de période |
| 3 | Valeur en dur | `DATE(aaaa, …)` ; colonne d'une table **reliée** comparée à un nombre (≥ 10), un libellé ou une liste ; division `/` par une expression |
| 3 | Documentation | Mesure visible sans description ; sans format (hors mesures qui renvoient du texte) |
| 3 | Modèle | Clé étrangère visible |
| 3 | Structure | Table sans relation (souvent normal : paramètre, table déconnectée) |

## Comment « utilisé » est calculé

1. Point de départ : tous les champs référencés dans les fichiers JSON du rapport (visuels, filtres de visuel, de page et de rapport, signets, mises en forme conditionnelles), les colonnes des relations, les rôles RLS, les groupes de calcul, les tables calculées (dont les paramètres de champs) et la clé de la table de dates.
2. Propagation : une mesure utilisée rend utilisées les mesures et colonnes de son DAX ; une colonne utilisée rend utilisée sa colonne de tri et le DAX d'une colonne calculée.

## `lean.py catalogue`

Même lecture du modèle et même calcul d'utilisation, restitués en dictionnaire de données (tables, colonnes, mesures et leur DAX, relations, rôles, objets visibles sans description) sur la sortie standard ; rien n'est écrit sur disque. Les adresses e-mail sont masquées partout (descriptions, DAX des mesures) et le filtre d'un rôle qui en contient une n'est pas recopié. **Seules les adresses e-mail** le sont : un nom de personne ou un identifiant `DOMAINE\compte` en dur est recopié — le signaler (`powerbi-governance`). L'OLS n'est pas restituée. Le type de table est déduit des préfixes de `powerbi-conventions` (`Fact_`, `Dim_`, `_Mesures`, `Param_`, `CG_`) ; vide sinon. Usage : skill `powerbi-documentation`.

## Limites

- **Un seul rapport** : les rapports connectés au modèle publié, les classeurs Excel et les requêtes externes ne sont pas visibles.
- Les références DAX non qualifiées `[X]` sont rattachées à une mesure si une mesure porte ce nom.
- `--changed` filtre **par fichier** : tous les constats d'une table modifiée sont montrés.
- Détection de doublons **exacte** (après normalisation) : les quasi-doublons demandent une lecture.
- Les heuristiques « valeur en dur » et « identifiant » sont des signaux à confirmer, pas des erreurs certaines.
