# Références visuelles

La boucle de références est ce qui rend les rapports « à nous » : l'agent connaît les bases, pas nos motifs. Chaque référence = **un motif précis** (une carte KPI, un graphique d'écart, un classement), **ses réglages exacts** et **une image** du résultat.

## Ajouter une référence

1. Trouver un visuel qui plaît (rapport interne, challenge communautaire, vidéo, Dribbble / Figma). Noter la **source** et vérifier qu'on peut s'en inspirer.
2. Si le fichier est disponible : l'enregistrer en **PBIP** dans un dossier `references/` hors du projet, puis demander à l'agent :
   > Ouvre le projet PBIP dans [dossier]. Trouve le visuel de la page « [page] » qui montre [description]. Explique comment il est construit : type, champs et mesures, mise en forme (couleurs, polices, bordures, marges), astuces (mise en forme conditionnelle, éléments masqués, superposition). Indique quels fichiers et quelles propriétés JSON contrôlent chaque partie.
3. Créer `visuals/<nom-du-motif>.md` à partir de [_template.md](_template.md) : quand l'utiliser, réglages du `visual.json` utiles, mesures en motifs génériques, piège éventuel.
4. Ajouter **l'image** dans `visuals/images/<nom-du-motif>.png` et la lier juste sous le titre. Sans image, les références deviennent floues.
5. Ajouter une ligne au catalogue ci-dessous, augmenter la version du plugin, commit.

Une référence courte et exacte vaut mieux qu'une longue : ne garder que ce qui reproduit le motif.

## Catalogue

| Motif | Quand l'utiliser | Fichier |
|---|---|---|
| Carte KPI avec comparaison | Chiffre principal + écart à l'objectif et à N-1 | [kpi-comparison-card.md](kpi-comparison-card.md) |
