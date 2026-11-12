# Interrupteurs (tables déconnectées)

Une page, plusieurs vues : au lieu de dupliquer les pages, l'utilisateur choisit la vue avec un petit segment en boutons. Mécanique :

1. une **petite table d'options**, sans relation avec le modèle (table déconnectée) ;
2. un **segment** sur cette table, style *Boutons*, **sélection unique** et **forcer la sélection** activés ;
3. des **mesures** qui lisent l'option avec `SELECTEDVALUE` ;
4. les **visuels, titres et couleurs** utilisent ces mesures.

Préférer un **paramètre de champs** quand il s'agit seulement de changer la mesure ou l'axe d'un visuel ; préférer une **table déconnectée** quand la logique, les titres ou les couleurs doivent suivre le choix.

Toujours donner une **valeur par défaut** à `SELECTEDVALUE` (cas où rien n'est sélectionné). Montrer le DAX à l'utilisateur **avant** de l'appliquer.

## Comparaison : Plan ou N-1

```dax
Param_Comparaison =
DATATABLE (
    "Comparaison", STRING,
    "Ordre", INTEGER,
    { { "Plan", 1 }, { "N-1", 2 } }
)
```

(Trier `Comparaison` par `Ordre` ; masquer `Ordre`.)

```dax
// QUOI : valeur de référence choisie par l'utilisateur (Plan ou N-1).
// COMMENT : lit Param_Comparaison ; N-1 par défaut.
// ADAPTER : [Objectif CA] et [CA HT N-1] selon le modèle.
CA comparaison =
SWITCH (
    SELECTEDVALUE ( Param_Comparaison[Comparaison], "N-1" ),
    "Plan", [Objectif CA],
    "N-1", [CA HT N-1]
)
```

```dax
CA écart comparaison =
VAR _reel = [CA HT]
VAR _ref = [CA comparaison]
RETURN
    IF ( NOT ISBLANK ( _reel ) && NOT ISBLANK ( _ref ), _reel - _ref )
```

```dax
CA atteinte % =
DIVIDE ( [CA HT], [CA comparaison] )
```

Titre dynamique (titre du visuel → *fx* → cette mesure) :

```dax
Titre tendance =
VAR _ref = SELECTEDVALUE ( Param_Comparaison[Comparaison], "N-1" )
VAR _atteinte = [CA atteinte %]
RETURN
    "Sommes-nous au-dessus " & IF ( _ref = "Plan", "du plan", "de N-1" ) & " ? "
        & IF ( _atteinte >= 1, "Oui", "Non" ) & ", "
        & FORMAT ( _atteinte, "0.0 %" )
```

Couleur conditionnelle (mise en forme → *fx* → valeur de champ) :

```dax
Couleur écart =
IF ( [CA écart comparaison] >= 0, "#2E7D32", "#C62828" )
```

## Classement : Haut ou Bas

```dax
Param_Sens =
DATATABLE ( "Sens", STRING, { { "Bas" }, { "Haut" } } )
```

```dax
// QUOI : rang du client selon l'écart, dans le sens choisi (5 pires ou 5 meilleurs).
// COMMENT : RANKX sur les clients visibles ; ignore les clients sans écart.
// ADAPTER : Dim_Client[Client] et la mesure d'écart.
Rang écart =
VAR _sens = SELECTEDVALUE ( Param_Sens[Sens], "Bas" )
VAR _clients =
    FILTER (
        ALLSELECTED ( Dim_Client[Client] ),
        NOT ISBLANK ( [CA écart comparaison] )
    )
RETURN
    IF (
        ISINSCOPE ( Dim_Client[Client] ) && NOT ISBLANK ( [CA écart comparaison] ),
        IF (
            _sens = "Haut",
            RANKX ( _clients, [CA écart comparaison],, DESC, DENSE ),
            RANKX ( _clients, [CA écart comparaison],, ASC, DENSE )
        )
    )
```

Sur la table : filtre de visuel `Rang écart` *est inférieur ou égal à* 5, tri par `Rang écart` croissant.

Titre : `"Quels clients sont " & IF ( SELECTEDVALUE ( Param_Sens[Sens], "Bas" ) = "Haut", "le plus au-dessus", "le plus en dessous" ) & " de la référence ?"`

## Vue : Mensuel ou Cumul

```dax
Param_Vue =
DATATABLE ( "Vue", STRING, "Ordre", INTEGER, { { "Mensuel", 1 }, { "Cumul", 2 } } )
```

```dax
CA vue =
SWITCH (
    SELECTEDVALUE ( Param_Vue[Vue], "Mensuel" ),
    "Mensuel", [CA HT],
    "Cumul", [CA HT YTD]
)
```

Même principe pour la référence : `CA comparaison vue` = N-1 mensuel ou `[CA HT YTD N-1]`.

## Pièges

- Une table déconnectée ne doit **jamais** recevoir de relation.
- Sans « forcer la sélection », plusieurs choix peuvent être cochés : `SELECTEDVALUE` renvoie alors la valeur par défaut.
- Nommer les tables `Param_…` et les masquer du rapport sauf la colonne utilisée par le segment.
