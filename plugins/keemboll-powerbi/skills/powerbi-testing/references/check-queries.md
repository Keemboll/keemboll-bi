# Requêtes DAX de contrôle

> **Non exécutées ici** : aucun moteur DAX n'était disponible à la rédaction. Chaque requête est à valider sur un modèle réel (DAX Studio ou vue Requête DAX de Power BI Desktop) avant d'être tenue pour fiable.

Modèle d'exemple : `Fact_Ventes` (`CustomerKey`, `DateCommande`, `Montant HT`), `Dim_Client` (`CustomerKey` clé de substitution, `CustomerCode` code métier), `Dim_Produit` (`Catégorie`), `Dim_Date` (`Date`, `Annee`, `AnneeMois`), `Dim_Magasin` (`Region`), mesure `[CA HT]`. Adapter les noms ; garder l'en-tête QUOI / ATTENDU.

Sauf mention contraire, **attendu = zéro ligne**.

## Niveau 1 — intégrité du modèle

### Clé en double dans une dimension

```dax
// QUOI : aucune clé en double dans Dim_Client.
// ATTENDU : zéro ligne.
EVALUATE
FILTER (
    SUMMARIZECOLUMNS ( Dim_Client[CustomerKey], "Nb lignes", COUNTROWS ( Dim_Client ) ),
    [Nb lignes] > 1
)
```

Si la relation existe déjà, le moteur garantit l'unicité côté « un » : ce test sert surtout avant de créer la relation, ou sur le code métier (`CustomerCode`, qui peut légitimement se répéter en SCD2 — voir `powerbi-data-modeling`).

### Clés vides dans les faits

```dax
// QUOI : aucune ligne de vente sans client ni date.
// ATTENDU : 0 et 0.
EVALUATE
ROW (
    "Sans client", COUNTROWS ( FILTER ( Fact_Ventes, ISBLANK ( Fact_Ventes[CustomerKey] ) ) ) + 0,
    "Sans date", COUNTROWS ( FILTER ( Fact_Ventes, ISBLANK ( Fact_Ventes[DateCommande] ) ) ) + 0
)
```

### Intégrité référentielle fait → dimension

```dax
// QUOI : toute clé client des ventes existe dans Dim_Client.
// ATTENDU : zéro ligne (sinon : liste des clés orphelines).
EVALUATE
EXCEPT (
    DISTINCT ( Fact_Ventes[CustomerKey] ),
    DISTINCT ( Dim_Client[CustomerKey] )
)
```

Variante qui pèse l'écart (lignes rattachées à la ligne vide de la dimension) :

```dax
// QUOI : poids des ventes sans client connu.
// ATTENDU : 0 ligne orpheline.
EVALUATE
ROW (
    "Lignes orphelines",
        COUNTROWS ( FILTER ( Fact_Ventes, ISBLANK ( RELATED ( Dim_Client[CustomerKey] ) ) ) ) + 0
)
```

Si la dimension porte une ligne « Inconnu » (clé −1, voir `powerbi-data-modeling`), les orphelins y sont rattachés en amont et ces tests ne les voient pas : compter aussi `COUNTROWS ( FILTER ( Fact_Ventes, Fact_Ventes[CustomerKey] = -1 ) ) + 0` et suivre ce nombre.

### Table de dates continue et couvrante

```dax
// QUOI : Dim_Date sans trou et couvrant toutes les dates de commande.
// ATTENDU : [Nb jours] = [Nb jours attendus] ; [Premier jour] <= [Min faits] ; [Dernier jour] >= [Max faits].
EVALUATE
VAR _min = MIN ( Dim_Date[Date] )
VAR _max = MAX ( Dim_Date[Date] )
RETURN
    ROW (
        "Premier jour", _min,
        "Dernier jour", _max,
        "Nb jours", COUNTROWS ( Dim_Date ),
        "Nb jours attendus", DATEDIFF ( _min, _max, DAY ) + 1,
        "Min faits", MIN ( Fact_Ventes[DateCommande] ),
        "Max faits", MAX ( Fact_Ventes[DateCommande] )
    )
```

Répéter pour chaque colonne de date reliée (`DateLivraison`…).

## Niveau 2 — rapprochement avec la source

```dax
// QUOI : totaux de contrôle mensuels à comparer à l'extraction du système source.
// ATTENDU : chaque ligne égale le total source du même mois, à la tolérance convenue.
EVALUATE
SUMMARIZECOLUMNS (
    Dim_Date[AnneeMois],
    "Nb lignes", COUNTROWS ( Fact_Ventes ),
    "Montant HT", SUM ( Fact_Ventes[Montant HT] )
)
ORDER BY Dim_Date[AnneeMois]
```

Comparer **nombre de lignes** et **montant** : le premier révèle les doublons de jointure et les filtres oubliés, le second les erreurs de signe ou de devise. Faire la comparaison hors dépôt ; ne noter que *conforme / non conforme*.

## Niveau 3 — mesures

### Total = somme des détails (mesures additives uniquement)

```dax
// QUOI : [CA HT] total égale la somme par catégorie.
// ATTENDU : [Ecart] = 0.
EVALUATE
VAR _total = [CA HT]
VAR _somme = SUMX ( VALUES ( Dim_Produit[Categorie] ), [CA HT] )
RETURN
    ROW ( "Total", _total, "Somme des détails", _somme, "Ecart", _total - _somme )
```

Avec `VALUES`, la ligne vide des faits orphelins est **incluse** dans la somme : un écart non nul signale une mesure non additive ou un filtre propre à la mesure, pas des orphelins. Pour peser les orphelins, remplacer `VALUES` par `DISTINCT ( Dim_Produit[Categorie] )`, qui exclut cette ligne vide : l'écart obtenu est alors leur montant.

### Cas connu

```dax
// QUOI : [CA HT] de l'année 2025 pour une catégorie donnée.
// ATTENDU : valeur communiquée par le métier (non écrite ici).
EVALUATE
CALCULATETABLE (
    ROW ( "CA HT", [CA HT] ),
    Dim_Date[Annee] = 2025,
    Dim_Produit[Categorie] = "Accessoires"
)
```

### Comportement aux bords

```dax
// QUOI : mesures sur une période sans vente (année hors historique).
// ATTENDU : [CA HT] vide, pas d'erreur, pas de 0 trompeur, pas d'infini.
EVALUATE
CALCULATETABLE (
    ROW ( "CA HT", [CA HT], "CA HT vide ?", ISBLANK ( [CA HT] ) ),
    Dim_Date[Annee] = 1999
)
```

Reprendre ce schéma pour : première année de l'historique (N-1 absent), dénominateur nul, sélection de plusieurs années, année en cours incomplète.

## Niveau 4 — non-régression

Comparer l'ancienne et la nouvelle formule dans la même requête, sans toucher au modèle :

```dax
// QUOI : la nouvelle écriture de [CA HT] donne les mêmes valeurs par mois et catégorie.
// ATTENDU : zéro ligne.
DEFINE
    MEASURE Fact_Ventes[CA HT nouveau] = SUM ( Fact_Ventes[Montant HT] )
EVALUATE
FILTER (
    SUMMARIZECOLUMNS (
        Dim_Date[AnneeMois],
        Dim_Produit[Categorie],
        "Avant", [CA HT],
        "Après", [CA HT nouveau]
    ),
    ABS ( [Avant] - [Après] ) > 0.005
        || ISBLANK ( [Avant] ) <> ISBLANK ( [Après] )
)
```

- Choisir des axes qui couvrent les filtres réellement utilisés par le rapport (`powerbi-lean`, commande `usage`).
- Pour un changement de modèle (relation, Power Query) : exécuter la même requête avant et après, exporter les deux résultats hors dépôt, comparer.

## Niveau 5 — RLS

À exécuter **sous le rôle testé** (DAX Studio connecté au modèle : options avancées de connexion, rôle / utilisateur effectif ; « Afficher comme » de Desktop pour le rapport).

```dax
// QUOI : identité vue par le moteur et périmètre visible pour le rôle RLS_Region.
// ATTENDU : seules les régions du profil de test ; total = somme de ces régions.
EVALUATE
ROW ( "Utilisateur", USERPRINCIPALNAME () )

EVALUATE
SUMMARIZECOLUMNS ( Dim_Magasin[Region], "CA HT", [CA HT] )
ORDER BY Dim_Magasin[Region]
```

```dax
// QUOI : utilisateur absent de la table de sécurité.
// ATTENDU : 0 ligne visible.
EVALUATE
ROW ( "Lignes visibles", COUNTROWS ( Fact_Ventes ) + 0 )
```

## Niveau 6 — rapport

Pas de requête générique : copier la requête du visuel depuis l'Analyseur de performances de Desktop, l'exécuter, et comparer aux valeurs testées aux niveaux 2 et 3. Vérifier à la main : segments, interactions entre visuels, signets, extraction, infobulles, états vides. Performance : `powerbi-performance`.
