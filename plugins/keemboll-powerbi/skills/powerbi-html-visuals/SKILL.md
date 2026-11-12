---
name: powerbi-html-visuals
description: "Création de visuels HTML et SVG dans les rapports Power BI à partir de mesures DAX : mini-graphiques (sparklines), barres de progression, indicateurs KPI, badges, bullet charts dans les tables et matrices (catégorie Image URL), et cartes HTML via le visuel personnalisé HTML Content. À utiliser quand un visuel natif ne suffit pas et qu'on veut générer du SVG ou du HTML en DAX, ou pour corriger un visuel SVG/HTML qui ne s'affiche pas. Triggers: HTML, SVG, sparkline, image URL, data URI, barre de progression, progress bar, KPI card, badge, HTML Content, visuel personnalisé, custom visual, infographie."
---

# Visuels HTML / SVG en DAX

Appliquer `powerbi-report-design` (couleurs du thème, accessibilité) et `powerbi-conventions` (nommage : préfixe `SVG ` ou `HTML ` pour ces mesures, dossier d'affichage `80 Visuels`). Surveiller le coût avec `powerbi-performance`.

## Deux techniques

| Technique | Rendu dans | Prérequis | Usage |
|---|---|---|---|
| **SVG en data URI** | Table, matrice, autres visuels acceptant une URL d'image dynamique | Mesure en catégorie **URL d'image** | Sparklines, barres, pastilles, flèches dans des lignes de tableau |
| **HTML** | Visuel personnalisé *HTML Content* (AppSource) | Visuels personnalisés autorisés par l'administrateur — **À ADAPTER** | Cartes KPI riches, blocs de texte mis en forme, listes |

Préférer d'abord les **visuels natifs** (mise en forme conditionnelle, icônes, barres de données, sparklines natives de table/matrice). Ne passer au SVG/HTML que si le natif ne permet pas le rendu voulu.

## Règles SVG

1. La mesure renvoie : `"data:image/svg+xml;utf8," & <svg …>`.
2. Définir la **catégorie de données = URL d'image** (Outils de mesure → Catégorie de données ; en TMDL : `dataCategory: ImageUrl`).
3. Utiliser des **apostrophes** pour les attributs SVG (`width='120'`) : les guillemets doivent être doublés en DAX.
4. Encoder `#` en **`%23`** dans les couleurs (`fill='%231F4E79'`) — sinon l'image est tronquée. Les autres caractères spéciaux (`%`, `<` dans du texte) doivent aussi être encodés ou évités.
5. Toujours `xmlns='http://www.w3.org/2000/svg'` et un `viewBox`.
6. Nombres formatés avec un **point décimal** : `FORMAT ( x, "0.0", "en-US" )` (un modèle en français produirait `12,5` → SVG invalide).
7. Taille d'image dans la table : Mise en forme → *Taille de l'image* (hauteur/largeur) cohérente avec le `viewBox`.
8. Couleurs issues de [theme-keemboll.json](../powerbi-report-design/references/theme-keemboll.json) ; jamais de couleur seule pour porter le sens.
9. Garder le SVG court (quelques centaines de caractères) : il est recalculé pour chaque cellule.

Modèles prêts à adapter : [references/svg-templates.md](references/svg-templates.md).

## Règles HTML (visuel HTML Content)

- Le visuel interprète du HTML + CSS en ligne ; **pas de JavaScript**.
- Construire le HTML dans une mesure (ou une colonne) et le placer dans le champ *Values*.
- **Échapper** les textes provenant des données (`&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`) avec `SUBSTITUTE` avant de les insérer.
- Styles en ligne, police et couleurs du thème ; largeur en `%` pour s'adapter au visuel.
- Prévoir un **texte alternatif** sur le visuel, le contenu HTML n'étant pas lu de façon fiable par les lecteurs d'écran.

Modèles : [references/html-templates.md](references/html-templates.md).

## Dépannage

| Symptôme | Cause probable |
|---|---|
| L'URL s'affiche en texte | Catégorie de données ≠ URL d'image |
| Image vide ou cassée | `#` non encodé, guillemets mal doublés, virgule décimale, `xmlns` absent |
| Image minuscule / rognée | Taille d'image de la table ≠ `viewBox` |
| Page lente | SVG long × beaucoup de lignes ; limiter les lignes ou simplifier |
| HTML brut affiché | Visuel natif utilisé au lieu de HTML Content |
