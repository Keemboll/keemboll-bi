---
name: powerbi-report-design
description: "Charte graphique et règles de conception des rapports Power BI : thème JSON (couleurs, polices), quatre questions par page, jetons de design (grille, cartes, couleurs), structure des pages, fonds SVG, références visuelles réutilisables, choix du bon visuel, titres et libellés, segments, infobulles, navigation et accessibilité (contraste, texte alternatif, ordre de tabulation). À utiliser pour planifier, créer, revoir ou harmoniser un rapport ou une page Power BI, en complément de powerbi-report-cli (mécanique PBIR). Triggers: rapport, report, page, dashboard, tableau de bord, charte, thème, theme, couleurs, mise en page, layout, visuel, graphique, accessibilité, design, maquette, fond de page, background, référence, revue de page."
---

# Design des rapports

> Charte par défaut **À ADAPTER** (couleurs et polices de la marque). La mécanique des fichiers PBIR, la prévisualisation et la publication sont gérées par `powerbi-report-cli` (Microsoft). Les visuels HTML/SVG relèvent de `powerbi-html-visuals`.

## Processus

1. **Quatre questions** : avant toute mise en page, écrire ce à quoi la page répond. Un visuel qui ne sert aucune question va sur une page de détail ou disparaît.
   1. **Comment avons-nous performé ?** Le chiffre principal, en haut à gauche.
   2. **Est-ce bien ?** Comparé à l'objectif et à N-1 — un chiffre sans comparaison ne dit rien.
   3. **Pourquoi ?** Qui ou quoi l'explique : quel mois, quelle catégorie, quel client / établissement.
   4. **Que faire ?** Le plus gros écart, où agir en premier (classement Bas / Haut).
2. **Plan de pages** : une page = un sujet. Lister les pages et leurs quatre réponses ; attendre la validation.
3. **Maquette HTML** de chaque page avec les champs réels du modèle → skill `powerbi-mockup`. Itérer sur la maquette (une phrase par changement) jusqu'à validation, **avant** de toucher au PBIP.
4. **Références** : chercher dans [references/visuals/](references/visuals/README.md) un motif validé pour chaque visuel (cartes KPI, écarts, classements…) et le réutiliser.
5. **Construire** dans le PBIP avec `powerbi-report-cli`, thème [references/theme-keemboll.json](references/theme-keemboll.json), jetons ci-dessous, fond SVG si besoin ([references/svg-backgrounds.md](references/svg-backgrounds.md)).
6. **Vérifier visuellement** : recharger dans Desktop (« Apply external changes », préversion, ou Desktop Bridge ; deux mécanismes distincts, voir `powerbi-tmdl`), capture d'écran, corriger alignements, données et libellés ; recommencer jusqu'à conformité.
7. **Contrôler** avec [references/accessibility-checklist.md](references/accessibility-checklist.md), puis **revue humaine** : chiffres contre la source. La validation des fichiers ne suffit pas.
8. **Capitaliser** : chaque correction notable devient une nouvelle référence dans `references/visuals/`.

Pour revoir une page existante sans la modifier : lister les **5 plus gros problèmes** (alignement, couleur, hiérarchie visuelle, encombrement, libellés), classés par impact, avec une correction proposée pour chacun.

## Jetons de design — À ADAPTER

| Décision | Valeur |
|---|---|
| Canevas | 1280 × 720 (standard) ou 1300 × 900 (tableau de bord dense) |
| Bande latérale (navigation, filtres) | 60 px, optionnelle |
| Marge extérieure / espace entre cartes | 20 px / 16 px |
| Cartes | fond blanc, rayon 12 px, bordure 1 px `#E5E7EB` |
| Fond de page | `#F5F6F8` |
| Couleur d'accent | **une seule** (`#1F4E79`) ; tout le reste en gris |
| Bon / mauvais | `#2E7D32` / `#C62828`, uniquement pour un écart à une référence |
| Texte titres / corps / discret | `#1F2933` / `#3C4650` / `#8A939B` |
| Polices | Segoe UI Semibold (titres), Segoe UI (corps) — **deux tailles qui comptent** : 12 pt titres, 10 pt le reste ; KPI 28 pt |

Ces valeurs doivent être identiques dans le thème, le fond SVG et la maquette HTML.

## Structure type d'une page (lecture en Z)

```
┌────┬─────────────────────────────────────────────────────────┐
│    │ Titre · période                [Plan | N-1]  [filtres] │
│ N  ├──────────┬──────────┬──────────┬──────────────────────┤
│ a  │ KPI 1 ★  │ KPI 2    │ KPI 3    │ KPI 4                │  Q1 + Q2
│ v  ├──────────┴──────────┴──┬───────┴──────────────────────┤
│    │ Tendance vs référence   │ Quels mois s'écartent ?      │  Q2 + Q3
│    ├─────────────────────────┼──────────────────────────────┤
│    │ Quels X sont en dessous?│ Quels Y sont en dessous ?    │  Q3 + Q4
│    │ [Bas | Haut]            │ [Bas | Haut]                 │
└────┴─────────────────────────┴──────────────────────────────┘
```

- Lecture en **Z** pour les tableaux de bord ; en **F** pour les pages surtout composées de tableaux et de texte.
- **KPI le plus important en haut à gauche.** Même taille = même importance : différencier exprès, jamais par accident.
- **Une page, plusieurs vues** : interrupteurs (Plan / N-1, Haut / Bas, Mensuel / Cumul) plutôt que des pages dupliquées → `powerbi-dax-library` (interrupteurs).
- **6 à 8 visuels** maximum (heuristique maison, pas une règle Microsoft) ; alignement strict sur la grille.

## Choisir le visuel

| Question | Visuel | Éviter |
|---|---|---|
| Évolution dans le temps | Courbe (continu), histogramme groupé (périodes discrètes) | Secteurs |
| Comparaison de catégories | Barres horizontales triées | 3D, radar |
| Part d'un tout (≤ 5 parts) | Barres 100 %, anneau à la rigueur | Secteurs > 5 parts |
| Écart à un objectif | Carte KPI avec cible, barres avec ligne de référence | Jauges multiples |
| Corrélation | Nuage de points | Double axe non justifié |
| Valeurs précises | Table / matrice avec mise en forme conditionnelle sobre | Tableaux de 50 colonnes |
| Géographie | Carte remplie (choroplèthe) si les zones sont connues | Bulles superposées |

## Règles de forme

- **Titres de visuels = question, avec la réponse** quand c'est possible (« Sommes-nous au-dessus de N-1 ? Non, 78 % »), via une mesure de titre dynamique.
- Unité et période visibles (titre, sous-titre ou étiquette).
- Trier les barres par valeur décroissante sauf ordre naturel (mois, tranches).
- Axe des valeurs à partir de 0 pour les barres/colonnes.
- Couleur = information : la couleur d'accent sert à **mettre en évidence**, le reste en gris/neutre. Rouge/vert réservés aux écarts (bon/mauvais), toujours doublés d'un signe ou d'une icône.
- Étiquettes de données plutôt que quadrillage quand il y a peu de points ; supprimer bordures, ombres et fonds superflus.
- Nombres abrégés (k, M) dans les KPI et axes ; précision complète en infobulle.

## Interactions et navigation

- Segments : 3 à 5 maximum par page, synchronisés seulement si nécessaire ; afficher les filtres actifs dans le sous-titre (mesure DAX de type texte).
- Boutons de navigation entre pages et signets pour les vues prédéfinies ; bouton « Réinitialiser les filtres ».
- Extraction (drill-through) vers une page de détail plutôt que des tables géantes.
- Infobulles de rapport pour le contexte (définition de la mesure, mini tendance).

## Livrables

- Plan de pages + croquis validés.
- Rapport avec thème appliqué.
- Checklist d'accessibilité complétée.
