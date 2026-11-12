# Carte KPI avec comparaison

> Image à ajouter : `images/carte-kpi-comparaison.png` (capture du premier rendu validé).

- **Quand l'utiliser** : questions 1 et 2 d'une page — « combien ? » et « est-ce bien ? ».
- **Déclencheurs** : KPI, carte, chiffre clé, vs objectif, vs N-1.
- **Source** : interne, inspiré des cartes « valeur + atteinte + écarts ».

## Construction

- Une carte par KPI, sur une carte du fond SVG (visuel transparent).
- Contenu, de haut en bas : libellé discret (10 pt, gris), **valeur** (28 pt), puis deux lignes « vs objectif » et « vs N-1 » avec écart en valeur et en %, coloré bon / mauvais **avec signe** (▲ / ▼).
- Option : anneau d'atteinte % à droite, sparkline 12 mois en bas.
- Réalisation :
  - **native** : visuel *Carte (nouvelle)* avec valeurs de référence ;
  - **riche** : une mesure HTML par carte dans le visuel *HTML Content* (voir `powerbi-html-visuals`, modèle « Carte KPI »), sparkline et anneau en SVG.
- Mesures : `[CA HT]`, `[Objectif CA]`, `[CA HT N-1]`, écarts et `%` (voir `powerbi-dax-library`), éventuellement `[CA comparaison]` si un interrupteur Plan / N-1 existe.

## Réglages clés

- Arrière-plan du visuel : désactivé ; bordure : aucune (le fond SVG porte la carte).
- Rembourrage intérieur : 12 px.
- Texte alternatif : mesure qui résume « CA HT 436 M€, 101 % de l'objectif, −24 % vs N-1 ».

## Piège

Valeur et comparaisons doivent réagir aux mêmes filtres : ne pas mélanger une mesure `ALL` dans la carte sans le signaler dans le libellé.
