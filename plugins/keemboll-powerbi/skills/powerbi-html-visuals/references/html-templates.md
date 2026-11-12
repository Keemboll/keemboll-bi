# Modèles HTML (visuel HTML Content)

Le visuel *HTML Content* (AppSource) affiche le HTML renvoyé par une mesure. CSS en ligne uniquement, pas de script. Vérifier que les visuels personnalisés sont autorisés dans le tenant.

## Carte KPI

```dax
HTML Carte CA =
VAR _ca = FORMAT ( [CA HT], "#,##0 €" )
VAR _evol = [CA HT Évol. %]
VAR _couleur = IF ( _evol >= 0, "#2E7D32", "#C62828" )
VAR _signe = IF ( _evol >= 0, "▲", "▼" )
RETURN
    "<div style='font-family:Segoe UI;padding:12px;border-left:4px solid #1F4E79;background:#FFFFFF'>"
        & "<div style='font-size:12px;color:#52606D'>Chiffre d'affaires HT</div>"
        & "<div style='font-size:28px;font-weight:600;color:#1F2933'>" & _ca & "</div>"
        & IF (
            NOT ISBLANK ( _evol ),
            "<div style='font-size:12px;color:" & _couleur & "'>" & _signe & " "
                & FORMAT ( ABS ( _evol ), "0.0 %" ) & " vs N-1</div>"
        )
        & "</div>"
```

Ici `#` n'a **pas** besoin d'être encodé : ce n'est pas une data URI.

## Liste Top 5 avec texte échappé

```dax
HTML Top 5 produits =
VAR _top =
    TOPN ( 5, ALLSELECTED ( Dim_Produit[Produit] ), [CA HT], DESC )
VAR _lignes =
    CONCATENATEX (
        _top,
        VAR _nom =
            SUBSTITUTE ( SUBSTITUTE ( SUBSTITUTE ( Dim_Produit[Produit], "&", "&amp;" ), "<", "&lt;" ), ">", "&gt;" )
        RETURN
            "<li style='display:flex;justify-content:space-between;padding:2px 0'>"
                & "<span>" & _nom & "</span>"
                & "<span style='font-weight:600'>" & FORMAT ( [CA HT], "#,##0 €" ) & "</span></li>",
        "",
        [CA HT], DESC
    )
RETURN
    "<ol style='font-family:Segoe UI;font-size:12px;margin:0;padding-left:18px;color:#1F2933'>"
        & _lignes & "</ol>"
```

## Bonnes pratiques

- Un visuel HTML = une mesure ; ne pas concaténer des pages entières.
- Utiliser les couleurs du thème `theme-keemboll.json`.
- Renseigner le texte alternatif du visuel (mesure DAX résumant le contenu).
- Si les visuels personnalisés sont interdits, revenir aux cartes natives + SVG.
