# Modèle et Power Query — détails

## Repères VertiPaq

- La taille d'une colonne dépend surtout de sa **cardinalité** (nombre de valeurs distinctes), pas du nombre de lignes.
- Signaux d'alerte dans VertiPaq Analyzer :
  - une colonne > 10–20 % de la taille du modèle ;
  - colonne `DateTime` avec heures/minutes/secondes sur une table de faits ;
  - clés texte longues ou GUID ;
  - tables cachées `LocalDateTable_…` (Date/heure automatique activée) ;
  - relations dont la taille dépasse celle des colonnes.

## Réduire la cardinalité

| Colonne | Action |
|---|---|
| Horodatage | Séparer `Date` (date) et `Heure` (arrondie au quart d'heure ou supprimée) |
| Montant à 6 décimales | Arrondir à 2 décimales, type décimal fixe |
| Identifiant texte | Clé de substitution entière, texte en dimension |
| Commentaire libre | Ne pas charger, ou dans une table de détail séparée en DirectQuery |

## Query folding

- Sources qui plient : SQL Server, Fabric Warehouse / SQL endpoint, Synapse, Oracle, PostgreSQL, OData partiellement.
- Étapes qui cassent souvent le pliage : `Table.Buffer`, ajout d'index, fusion avec une autre source, certaines fonctions texte personnalisées.
- Vérification : clic droit → *Afficher la requête native* (grisé = pas de pliage), ou indicateurs d'étapes dans Power Query Online.

## Actualisation incrémentielle

1. Créer les paramètres `RangeStart` et `RangeEnd` (type Date/Heure, valeurs d'exemple).
2. Filtrer la table : `each [DateCommande] >= RangeStart and [DateCommande] < RangeEnd` (inégalité stricte d'un côté pour éviter les doublons).
3. Vérifier que le filtre **plie** vers la source.
4. Définir la stratégie (ex. archiver 5 ans, actualiser les 10 derniers jours) — **À ADAPTER**.

## Direct Lake (Fabric)

- Optimiser les tables Delta : V-Order, `OPTIMIZE`, taille de fichiers raisonnable, peu de petits fichiers.
- Préférer **Direct Lake on OneLake** pour les nouveaux modèles : pas de repli DirectQuery, pas de dépendance au point de terminaison SQL.
- Éviter les vues SQL non matérialisées : sur OneLake elles ne sont pas prises en charge ; sur le point de terminaison SQL elles provoquent un repli DirectQuery. Matérialiser la vue en table Delta.
- Surveiller les garde-fous de la capacité (fichiers Parquet, groupes de lignes, lignes) : sur le point de terminaison SQL, leur dépassement provoque un repli DirectQuery (propriété `DirectLakeBehavior`) ; sur OneLake, la requête échoue (les visuels ne s'affichent pas).
- Repli sur le point de terminaison SQL : `EVALUATE TABLETRAITS ()` donne la cause par table dans la colonne `DirectLakeFallbackInfo` (`None` = Direct Lake).

## DirectQuery

- Indexes / statistiques côté source, vues pré-agrégées.
- Tables d'agrégation en Import (fonction *Gérer les agrégations*).
- Dimensions en mode **Dual**.
- Limiter les visuels par page et activer la réduction des requêtes.
