# RLS et OLS — exemples et pièges

Modèle d'exemple : `Fact_Ventes` → `Dim_Magasin[Region]`, table de sécurité `Dim_Utilisateur[Email]`, `Dim_Utilisateur[Region]` (masquée). Noms de tables et préfixes : voir `powerbi-conventions`. Les adresses sont fictives (`@example.com`).

> Ces exemples n'ont pas été exécutés ici (aucun moteur disponible) : les tester selon `powerbi-testing` avant usage.

## RLS statique

Un rôle par périmètre. Simple, mais à multiplier dès que les périmètres changent.

```tmdl
role RLS_RegionNord
	modelPermission: read

	tablePermission Dim_Magasin = Dim_Magasin[Region] = "Nord"
```

## RLS dynamique — un périmètre par utilisateur

```tmdl
role RLS_Region
	modelPermission: read

	tablePermission Dim_Magasin = Dim_Magasin[Region] = LOOKUPVALUE ( Dim_Utilisateur[Region], Dim_Utilisateur[Email], USERPRINCIPALNAME () )

	tablePermission Dim_Utilisateur = Dim_Utilisateur[Email] = USERPRINCIPALNAME ()
```

- `LOOKUPVALUE` renvoie une erreur si l'utilisateur a **plusieurs** lignes : n'utiliser cette forme que si la table de sécurité a une ligne par utilisateur.
- Utilisateur absent de la table : `LOOKUPVALUE` renvoie BLANK, aucune région ne correspond, il ne voit rien — c'est le comportement voulu.

## RLS dynamique — plusieurs périmètres par utilisateur

Expression du filtre posé sur `Dim_Magasin` :

```dax
Dim_Magasin[Region]
    IN CALCULATETABLE (
        VALUES ( Dim_Utilisateur[Region] ),
        Dim_Utilisateur[Email] = USERPRINCIPALNAME ()
    )
```

`Dim_Utilisateur` reste **déconnectée** du reste du modèle (pas de relation) : le filtre passe par l'expression, pas par une relation.

## Hiérarchie (un responsable voit son équipe)

Avec une dimension `Dim_Employe` portant `EmployeKey`, `ResponsableKey` et `Email`, et une colonne calculée de chemin :

```dax
Chemin = PATH ( Dim_Employe[EmployeKey], Dim_Employe[ResponsableKey] )
```

Filtre du rôle sur `Dim_Employe` :

```dax
PATHCONTAINS (
    Dim_Employe[Chemin],
    LOOKUPVALUE ( Dim_Employe[EmployeKey], Dim_Employe[Email], USERPRINCIPALNAME () )
)
```

## `USERPRINCIPALNAME()` ou `USERNAME()`

Préférer `USERPRINCIPALNAME()` : il renvoie l'UPN (`prenom.nom@example.com`) dans le service comme dans Desktop, alors que `USERNAME()` renvoie `DOMAINE\utilisateur` dans Desktop. La comparaison de chaînes DAX est insensible à la casse, mais l'UPN peut différer de l'adresse e-mail : alimenter la table de sécurité avec l'**UPN**.

## OLS

Extrait : ces `tablePermission` s'**ajoutent** à celles du rôle `RLS_Region` ci-dessus (RLS et OLS dans le même rôle), elles ne le remplacent pas.

```tmdl
role RLS_Region
	modelPermission: read

	tablePermission Fact_Ventes
		columnPermission 'Cout unitaire' = none

	tablePermission Dim_Salaire
		metadataPermission: none
```

- `columnPermission … = none` masque une colonne (forme abrégée ; la forme longue place `metadataPermission: none` sous `columnPermission <colonne>`) ; `metadataPermission: none` sous `tablePermission` masque la table entière. Non exécuté ici : vérifier en exportant un rôle existant (vue TMDL de Desktop) ; la syntaxe TMDL fait foi dans `powerbi-tmdl` et la documentation Microsoft.
- Pour ce rôle, toute mesure qui référence l'objet masqué échoue, ainsi que les visuels qui l'utilisent : prévoir des mesures et des pages séparées, ou une page conditionnée.
- Une relation qui s'appuie sur une colonne masquée continue de fonctionner tant que sa table n'est pas masquée. En revanche, masquer une **table** située au milieu d'une chaîne de relations (A → B → C, B masquée) est refusé à la conception.

## Pièges fréquents

| Piège | Conséquence | Parade |
|---|---|---|
| Filtre posé sur la table de faits | Lent (évalué sur la plus grande table) ; les dimensions restent entièrement visibles (noms de clients, de magasins dans les segments) | Filtrer la dimension |
| Relation bidirectionnelle sans option de sécurité | Le filtre de rôle ne remonte pas | Filtrer la bonne dimension, ou cocher l'option en connaissance de cause |
| Utilisateur dans deux rôles | Il voit l'union des deux périmètres | Un seul rôle dynamique |
| Test fait par un Admin / Membre / Contributeur dans le service | La RLS ne s'applique pas à lui : test faussement rassurant | Tester « en tant que » rôle, ou avec un compte Lecteur |
| Mesure avec `ALL ( Dim_Magasin )` | Ne contourne **pas** la RLS (le filtre de sécurité reste), mais les totaux « tous magasins » deviennent « tous **mes** magasins » | Le dire dans la description de la mesure |
| Table de sécurité visible et non filtrée | Chacun lit les droits de tous | La masquer **et** la filtrer par le rôle |
| E-mails en dur dans l'expression | Données personnelles dans Git, maintenance impossible | Table de sécurité + groupes |
| Rôle créé mais sans membres dans le service | Les lecteurs non rattachés à un rôle ne voient rien dès qu'un rôle existe | Rattacher des groupes ; le noter dans `SECURITY_MODEL.md` |
| Modèle composite / DirectQuery vers un autre modèle | Règles de la source et du modèle se cumulent de façon non évidente | Vérifier la documentation Microsoft et tester |
