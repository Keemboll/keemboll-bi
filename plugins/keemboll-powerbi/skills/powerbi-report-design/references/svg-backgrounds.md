# Fonds de page SVG

Un bon fond porte les **cartes, bordures et la bande latérale** : les visuels posés dessus restent simples (fond et bordure transparents). Le fond est une image SVG à la taille exacte du canevas.

## Processus

1. Partir de la **maquette HTML validée** (`powerbi-mockup`) ou d'une capture d'un rapport de référence.
2. Lire les positions et tailles des visuels de la page (`*.Report/definition/pages/<page>/visuals/*/visual.json` → `position`).
3. Générer un SVG à la taille du canevas, avec une carte par zone, en respectant les **jetons de design** (rayon, bordure, marges, couleurs).
4. Enregistrer le fichier dans le projet (ex. `*.Report/StaticResources/RegisteredResources/fond-<page>.svg` via `powerbi-report-cli`) et le définir comme **arrière-plan de la page**, ajustement *Ajuster*, transparence 0 %.
5. Rendre les visuels transparents (arrière-plan désactivé, pas de bordure) et vérifier l'alignement par capture d'écran.

## Gabarit (1280 × 720, bande latérale 60 px, 4 KPI + 2 + 2)

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
  <rect width="1280" height="720" fill="#F5F6F8"/>
  <rect width="60" height="720" fill="#1F4E79"/>
  <!-- Ligne KPI : y=80, h=130 ; largeur utile 1280-60-2*20 = 1180 ; 4 cartes, 3 espaces de 16 -->
  <g fill="#FFFFFF" stroke="#E5E7EB" stroke-width="1">
    <rect x="80"  y="80" width="283" height="130" rx="12"/>
    <rect x="379" y="80" width="283" height="130" rx="12"/>
    <rect x="678" y="80" width="283" height="130" rx="12"/>
    <rect x="977" y="80" width="283" height="130" rx="12"/>
    <rect x="80"  y="226" width="582" height="220" rx="12"/>
    <rect x="678" y="226" width="582" height="220" rx="12"/>
    <rect x="80"  y="462" width="582" height="238" rx="12"/>
    <rect x="678" y="462" width="582" height="238" rx="12"/>
  </g>
</svg>
```

Règles de calcul : largeur d'une carte = (largeur utile − (n − 1) × espace) / n ; garder les mêmes coordonnées que les visuels (le visuel occupe la carte avec une marge intérieure de 8 à 12 px).

## Points d'attention

- Les positions dans le SVG et dans les `visual.json` doivent être **identiques** : toute modification de mise en page impose de régénérer le fond.
- Pas de texte dans le fond (non accessible, non traduisible) : les titres restent dans les visuels ou des zones de texte.
- Garder le SVG simple (quelques kilo-octets).
- Alternative graphique : concevoir le fond dans Figma (certains agents disposent d'un connecteur Figma) puis l'exporter en SVG.
