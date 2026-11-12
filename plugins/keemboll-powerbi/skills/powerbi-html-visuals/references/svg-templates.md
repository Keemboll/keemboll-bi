# Modèles SVG (DAX)

Remplacer `[CA HT]`, `[Objectif CA]`, `Dim_Date` par les objets du modèle. Toutes ces mesures : catégorie de données **URL d'image**, dossier `80 Visuels`.

## Barre de progression vers un objectif

```dax
SVG Progression objectif =
VAR _pct = MIN ( MAX ( DIVIDE ( [CA HT], [Objectif CA] ), 0 ), 1 )
VAR _w = FORMAT ( _pct * 100, "0.0", "en-US" )
VAR _couleur = IF ( _pct >= 1, "%232E7D32", "%231F4E79" )
VAR _label = FORMAT ( DIVIDE ( [CA HT], [Objectif CA] ), "0 %", "en-US" )
RETURN
    IF (
        NOT ISBLANK ( [Objectif CA] ),
        "data:image/svg+xml;utf8,"
            & "<svg xmlns='http://www.w3.org/2000/svg' width='140' height='20' viewBox='0 0 140 20'>"
            & "<rect x='0' y='4' width='100' height='12' rx='3' fill='%23E5E7EB'/>"
            & "<rect x='0' y='4' width='" & _w & "' height='12' rx='3' fill='" & _couleur & "'/>"
            & "<text x='106' y='15' font-family='Segoe UI' font-size='11' fill='%231F2933'>"
            & SUBSTITUTE ( _label, "%", "%25" )
            & "</text></svg>"
    )
```

## Sparkline 12 mois

```dax
SVG Sparkline CA =
VAR _w = 120
VAR _h = 30
VAR _mois =
    CALCULATETABLE (
        ADDCOLUMNS (
            SUMMARIZE ( Dim_Date, Dim_Date[Annee], Dim_Date[MoisNum] ),
            "@k", Dim_Date[Annee] * 12 + Dim_Date[MoisNum],
            "@v", [CA HT]
        ),
        DATESINPERIOD ( Dim_Date[Date], MAX ( Dim_Date[Date] ), -12, MONTH )
    )
VAR _kMin = MINX ( _mois, [@k] )
VAR _kMax = MAXX ( _mois, [@k] )
VAR _vMin = MINX ( _mois, [@v] )
VAR _vMax = MAXX ( _mois, [@v] )
VAR _points =
    CONCATENATEX (
        _mois,
        FORMAT ( DIVIDE ( [@k] - _kMin, _kMax - _kMin ) * ( _w - 4 ) + 2, "0.0", "en-US" )
            & ","
            & FORMAT ( _h - 2 - DIVIDE ( [@v] - _vMin, _vMax - _vMin ) * ( _h - 4 ), "0.0", "en-US" ),
        " ",
        [@k], ASC
    )
RETURN
    IF (
        COUNTROWS ( _mois ) > 1,
        "data:image/svg+xml;utf8,"
            & "<svg xmlns='http://www.w3.org/2000/svg' width='" & _w & "' height='" & _h
            & "' viewBox='0 0 " & _w & " " & _h & "'>"
            & "<polyline fill='none' stroke='%231F4E79' stroke-width='2' stroke-linejoin='round' points='"
            & _points
            & "'/></svg>"
    )
```

Fonctionne car `Dim_Date` est marquée comme table de dates : le filtre `DATESINPERIOD` sur `Dim_Date[Date]` remplace les filtres de la ligne courante (mois, année).

## Flèche d'évolution N-1

```dax
SVG Tendance =
VAR _evol = [CA HT Évol. %]
VAR _hausse = _evol >= 0
VAR _couleur = IF ( _hausse, "%232E7D32", "%23C62828" )
VAR _forme =
    IF (
        _hausse,
        "<polygon points='8,2 14,12 2,12' fill='" & _couleur & "'/>",
        "<polygon points='2,4 14,4 8,14' fill='" & _couleur & "'/>"
    )
RETURN
    IF (
        NOT ISBLANK ( _evol ),
        "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 16 16'>"
            & _forme & "</svg>"
    )
```

La forme (haut/bas) porte le sens en plus de la couleur — conforme à l'accessibilité.

## Bullet chart (réel / objectif / N-1)

```dax
SVG Bullet =
VAR _reel = [CA HT]
VAR _objectif = [Objectif CA]
VAR _n1 = [CA HT N-1]
VAR _max = MAX ( MAX ( _reel, _objectif ), _n1 )
VAR _echelle = 130
VAR _xReel = FORMAT ( DIVIDE ( _reel, _max ) * _echelle, "0.0", "en-US" )
VAR _xObjectif = FORMAT ( COALESCE ( DIVIDE ( _objectif, _max ), 0 ) * _echelle, "0.0", "en-US" )
VAR _xN1 = FORMAT ( COALESCE ( DIVIDE ( _n1, _max ), 0 ) * _echelle, "0.0", "en-US" )
RETURN
    IF (
        NOT ISBLANK ( _reel ),
        "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='20' viewBox='0 0 140 20'>"
            & "<rect x='0' y='2' width='" & _xN1 & "' height='16' fill='%23E5E7EB'/>"
            & "<rect x='0' y='7' width='" & _xReel & "' height='6' fill='%231F4E79'/>"
            & "<rect x='" & _xObjectif & "' y='3' width='2' height='14' fill='%23E76F51'/>"
            & "</svg>"
    )
```

Fond gris = N-1, barre bleue = réel, trait orange = objectif.

## Pastille de statut

```dax
SVG Statut =
VAR _couleur =
    SWITCH (
        TRUE (),
        [Marge brute %] >= 0.30, "%232E7D32",
        [Marge brute %] >= 0.15, "%23E9C46A",
        "%23C62828"
    )
RETURN
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'>"
        & "<circle cx='6' cy='6' r='5' fill='" & _couleur & "'/></svg>"
```

Seuils **À ADAPTER**. Afficher la valeur dans une colonne voisine (la couleur seule ne suffit pas).
