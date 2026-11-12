---
name: powerbi-tmdl
description: "Lecture et édition de modèles sémantiques Power BI au format TMDL (Tabular Model Definition Language) dans un projet PBIP : syntaxe, indentation, tables, colonnes, mesures, relations, partitions Power Query, groupes de calcul, rôles RLS, descriptions et vérification. À utiliser dès qu'on lit, écrit, compare ou corrige des fichiers .tmdl ou un dossier *.SemanticModel/definition, ou qu'on travaille dans la vue TMDL de Power BI Desktop. Triggers: TMDL, .tmdl, PBIP, SemanticModel, definition, model.tmdl, relationships.tmdl, vue TMDL, createOrReplace, git, diff de modèle."
---

# TMDL — édition de modèles sémantiques

Appliquer `powerbi-conventions` (nommage, descriptions, validation). Pour la publication vers Fabric/Power BI Service, déléguer à `semantic-model-authoring` (Microsoft).

## Structure d'un projet PBIP

```
MonRapport.pbip
MonRapport.SemanticModel/
├── definition.pbism
└── definition/
    ├── database.tmdl          # niveau de compatibilité
    ├── model.tmdl             # options du modèle, culture, ordre des tables (ref table …)
    ├── relationships.tmdl     # toutes les relations
    ├── expressions.tmdl       # paramètres et requêtes M partagées
    ├── tables/<Table>.tmdl    # une table par fichier : colonnes, mesures, partitions, hiérarchies
    ├── roles/<Role>.tmdl      # RLS
    └── cultures/<langue>.tmdl # traductions / synonymes Q&A
MonRapport.Report/             # rapport (PBIR) → voir powerbi-report-cli
```

## Règles de syntaxe essentielles

- **Indentation = structure.** Utiliser des **tabulations**, de façon cohérente : objet au niveau N, ses propriétés au niveau N+1, une expression multiligne au niveau N+2.
- Déclaration : `<type> <Nom>` ; avec expression : `<type> <Nom> = <expression>`.
- Noms avec espaces ou caractères spéciaux entre **apostrophes** : `measure 'CA HT'` ; une apostrophe dans le nom se double : `'Chiffre d''affaires'`.
- Propriétés : `nom: valeur` ; booléen vrai = propriété seule (`isHidden`) ; faux = `isActive: false`.
- **Descriptions** : lignes `///` juste au-dessus de l'objet.
- Références de colonnes dans les relations : `Table.Colonne`, avec apostrophes si besoin (`Fact_Ventes.'Date commande'`).
- `lineageTag` : **ne jamais copier** celui d'un autre objet. Pour un nouvel objet, l'omettre (Power BI Desktop le génère) ou créer un GUID neuf.

Exemples complets : [references/syntax.md](references/syntax.md).

## Processus d'édition

1. **Synchronisation avec Power BI Desktop** (versions récentes de Desktop) : **enregistrer** dans Desktop avant d'écrire (l'agent lit les fichiers sur disque, pas la fenêtre). Deux mécanismes distincts :
   - **Rechargement des changements externes** (fonction en **préversion**, Desktop d'**août 2026 ou plus récent**) : activer *Detect and reload external PBIP changes* (Options → Fonctionnalités en préversion, puis redémarrer Desktop). Après écriture, Desktop propose d'**appliquer les changements externes**. Sur une version plus ancienne ou sans cette option : **fermer Desktop** avant d'écrire.
   - **Desktop Bridge** (rechargement programmatique et captures d'écran pour l'agent) : *Enable external tool access to Power BI Desktop through secure local APIs* dans Options → **Sécurité** → Desktop Bridge, **activé par défaut** ; la documentation le signale aussi comme préversion.

   Dans tous les cas, ne jamais enregistrer depuis Desktop pendant que l'agent écrit (écrasement).
2. Vérifier que le projet est sous **Git** et que l'arbre est propre (`git status`) pour pouvoir revenir en arrière.
3. Lire `model.tmdl`, `relationships.tmdl` et les tables concernées avant d'écrire.
4. Proposer les modifications (diff) et **attendre la validation** pour toute suppression, renommage ou changement de relation.
5. Écrire en respectant l'indentation existante du fichier (tabulations).
6. Ajout de table : créer `tables/<Nom>.tmdl` et, si `model.tmdl` contient des lignes `ref table …`, y ajouter `ref table <Nom>`.
7. **Renommage** : mettre à jour toutes les références (mesures DAX, relations, `sortByColumn`, hiérarchies, rôles, cultures, rapport PBIR). Rechercher l'ancien nom dans tout le dossier `definition/` **et** dans `*.Report/`.
8. Appliquer les changements externes (ou rouvrir le `.pbip`) : les erreurs de syntaxe s'affichent au chargement. Corriger puis vérifier les valeurs avec une requête DAX.
9. `git diff` pour relire, puis commit.

## Vue TMDL de Power BI Desktop

Alternative sans fermer Desktop : onglet **Vue TMDL** → glisser un objet depuis le volet Données pour générer son script `createOrReplace`, le modifier, puis **Appliquer**. Pratique pour des modifications ciblées ; les fichiers PBIP sont mis à jour à l'enregistrement.

## Pièges fréquents

| Erreur | Cause | Correction |
|---|---|---|
| Fichier refusé à l'ouverture | Mélange espaces / tabulations | Ré-indenter avec des tabulations |
| Mesure sur une seule ligne tronquée | Expression multiligne pas assez indentée | Expression au niveau propriétés + 1 |
| Relation ignorée | Colonnes de types différents ou nom mal cité | Vérifier `dataType` et les apostrophes |
| Doublon de lineageTag | Copier-coller d'un objet existant | Supprimer la ligne `lineageTag` du nouvel objet |
| Visuels cassés après renommage | Références PBIR non mises à jour | Rechercher l'ancien nom dans `*.Report/` |
