---
name: powerbi-mockup
description: "Maquette HTML d'une page de rapport Power BI construite à partir du modèle sémantique réel, avant toute construction dans Power BI : inventaire des tables, mesures et colonnes, page HTML autonome au format du canevas, chaque élément étiqueté avec le champ exact qu'il utilisera, liste des mesures manquantes, itérations rapides, puis passage au PBIP. À utiliser pour planifier ou prototyper une page, comparer des variantes de mise en page ou préparer la construction d'un rapport. Triggers: maquette, mock-up, mockup, prototype, wireframe, HTML, planifier une page, esquisse de rapport, layout, avant de construire."
---

# Maquette HTML depuis le modèle

Changer une mise en page dans Power BI prend du temps ; dans une maquette HTML, une phrase suffit. On itère ici jusqu'à validation, **puis** on construit. Appliquer `powerbi-report-design` (quatre questions, jetons de design) et `powerbi-conventions` (confidentialité des métadonnées).

## Processus

1. **Lire le modèle** (`*.SemanticModel/definition/` ou modèle publié via MCP) et produire l'**inventaire** : tables, mesures (avec dossier et format), colonnes clés des dimensions, table de dates. Le montrer une fois à l'utilisateur.
2. **Quatre questions** de la page (voir `powerbi-report-design`) : les faire confirmer.
3. **Associer** chaque question à des éléments (cartes KPI, tendance, écarts, classements) et à des **champs existants**. Si un champ manque : **ne pas l'inventer**, l'ajouter à la liste « Mesures manquantes » avec une proposition de DAX (`powerbi-dax-library`).
4. **Générer un seul fichier HTML** autonome (CSS et JS en ligne, aucune ressource externe) à partir de [references/mockup-template.html](references/mockup-template.html) :
   - taille exacte du canevas et jetons de design (couleurs, rayon, marges) ;
   - **chaque élément porte une étiquette** `Table[Champ]` / `[Mesure]` (attribut `data-fields` + texte visible discret) ;
   - titres formulés en **questions** ;
   - valeurs d'exemple **plausibles et fictives** (jamais de vraies données copiées depuis le cache) ;
   - interrupteurs (Plan / N-1, Haut / Bas, Mensuel / Cumul) et volet de filtres simulés si prévus ;
   - encadré final « Mesures manquantes » et « Hypothèses ».
5. **Enregistrer** à côté du projet : `maquettes/<page>-v1.html` ; l'utilisateur l'ouvre dans le navigateur.
6. **Itérer** : une demande = une nouvelle version (`-v2`, `-v3`) ; conserver les étiquettes de champs. Changements typiques : ordre et taille, type de graphique (anneau → barres triées), titres-questions, couleurs (un accent, vert / rouge pour bon / mauvais), interrupteurs.
7. **Valider** avec la [checklist](references/mockup-checklist.md), puis passer à la construction.

## Passage au PBIP

Demande type à exécuter avec `powerbi-report-cli` :

> Construis la maquette `maquettes/<page>-vN.html` comme nouvelle page du projet PBIP [chemin]. Respecte la mise en page, les tailles et les couleurs. Utilise les étiquettes de champs de la maquette pour lier chaque visuel au modèle. Si un champ ou une mesure n'existe pas, liste-le au lieu de deviner. Valide les fichiers du rapport, recharge le rapport dans Power BI Desktop, fais une capture d'écran de la page et corrige ce qui ne va pas : données, visuels, alignement.

Puis `powerbi-report-design` étape 6 (vérification visuelle) et capitalisation des corrections en références.

## Règles

- La maquette n'utilise **que des champs qui existent** ; tout le reste est explicitement marqué manquant.
- Une maquette = une page. Pas de framework, pas de CDN : un fichier qui s'ouvre hors ligne.
- Données d'exemple fictives : ne jamais lire `.pbi/cache.abf` ni recopier des valeurs réelles, surtout pour des données sensibles.
- Ne pas modifier le PBIP pendant la phase de maquette.
