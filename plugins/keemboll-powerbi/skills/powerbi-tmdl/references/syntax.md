# TMDL — exemples de référence

Les exemples sont indentés avec de vraies **tabulations**, comme les fichiers générés par Power BI Desktop.

## Table de faits avec mesures, colonnes et partition

```tmdl
table Fact_Ventes

	/// Chiffre d'affaires hors taxes. Source : Fact_Ventes[Montant HT].
	measure 'CA HT' = SUM ( Fact_Ventes[Montant HT] )
		formatString: #,##0 €
		displayFolder: 01 Ventes

	/// Marge brute en % du CA HT.
	measure 'Marge brute %' =
			VAR _ca = [CA HT]
			RETURN
			    DIVIDE ( [Marge brute], _ca )
		formatString: 0.0 %
		displayFolder: 02 Marge

	column ProductKey
		dataType: int64
		isHidden
		summarizeBy: none
		sourceColumn: ProductKey

	column 'Montant HT'
		dataType: decimal
		formatString: #,##0.00 €
		summarizeBy: sum
		sourceColumn: Montant HT

	column DateCommande
		dataType: dateTime
		formatString: dd/MM/yyyy
		summarizeBy: none
		sourceColumn: DateCommande

	partition Fact_Ventes = m
		mode: import
		source =
				let
				    Source = Sql.Database(ServeurSql, BaseSql),
				    Ventes = Source{[Schema = "gold", Item = "fact_ventes"]}[Data]
				in
				    Ventes
```

`ServeurSql` et `BaseSql` sont des paramètres définis dans `expressions.tmdl` (jamais de valeur en dur dans la partition).

## Paramètres (expressions.tmdl)

```tmdl
expression ServeurSql = "monserveur.datawarehouse.fabric.microsoft.com" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]

expression BaseSql = "wh_gold" meta [IsParameterQuery = true, Type = "Text", IsParameterQueryRequired = true]
```

## Table de dates marquée

```tmdl
table Dim_Date
	dataCategory: Time

	column Date
		dataType: dateTime
		isKey
		formatString: dd/MM/yyyy
		summarizeBy: none
		sourceColumn: Date

	column Mois
		dataType: string
		summarizeBy: none
		sourceColumn: Mois
		sortByColumn: MoisNum

	column MoisNum
		dataType: int64
		isHidden
		summarizeBy: none
		sourceColumn: MoisNum

	hierarchy Calendrier
		level Annee
			column: Annee
		level Mois
			column: Mois
```

## Relations (relationships.tmdl)

`fromColumn` = côté **plusieurs** (fait), `toColumn` = côté **un** (dimension).

```tmdl
relationship 8f4b2c1e-0d6a-4f3b-9c55-2a1e7d3b9f10
	fromColumn: Fact_Ventes.DateCommande
	toColumn: Dim_Date.Date

relationship 1c9e7a52-6b3d-4e8f-a210-5d4c3b2a1f09
	isActive: false
	fromColumn: Fact_Ventes.DateLivraison
	toColumn: Dim_Date.Date

relationship 5a2d8e7f-3c1b-4a9e-8d6f-7b0c2e4a6d13
	crossFilteringBehavior: bothDirections
	fromColumn: Bridge_ClientCompte.CompteKey
	toColumn: Dim_Compte.CompteKey
```

Le nom d'une relation est un identifiant libre (GUID conseillé, unique).

## Mesure à chaîne de format dynamique

```tmdl
	measure 'Valeur sélectionnée' = SELECTEDMEASURE ()
		formatStringDefinition = SELECTEDMEASUREFORMATSTRING ()
```

## Rôle RLS (roles/RLS_Region.tmdl)

```tmdl
role RLS_Region
	modelPermission: read

	tablePermission Dim_Magasin = Dim_Magasin[Region] = LOOKUPVALUE ( Dim_Utilisateur[Region], Dim_Utilisateur[Email], USERPRINCIPALNAME () )
```

## Groupes de calcul

Plus sûr de les **créer** dans Power BI Desktop (Modélisation → Groupe de calcul) puis d'éditer les éléments en TMDL. Forme d'un élément :

```tmdl
		calculationItem YTD = CALCULATE ( SELECTEDMEASURE (), DATESYTD ( Dim_Date[Date] ) )
```

## Expressions multilignes verbatim

Pour conserver exactement les espaces d'une expression, l'encadrer de trois backticks :

````tmdl
	measure 'Exemple' = ```
			VAR _x = 1
			RETURN _x
			```
````
