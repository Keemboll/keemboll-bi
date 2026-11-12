# Modèle de `SECURITY_MODEL.md`

Copier le bloc ci-dessous à la racine du projet, à côté du `.pbip`. **Aucun nom de personne, aucun e-mail, aucune valeur de donnée** : des fonctions, des noms de groupes, des périmètres.

```markdown
# Sécurité — <nom du projet>

Dernière mise à jour : AAAA-MM-JJ

## Fiche

| Élément | Valeur |
|---|---|
| Propriétaire métier (fonction) | <ex. Direction commerciale> |
| Propriétaire technique (fonction) | <ex. Équipe BI> |
| Classification des données | <publique / interne / confidentielle / personnelle / santé> |
| Étiquette de sensibilité | <nom de l'étiquette> |
| Endossement | <aucun / promu / certifié> — depuis le AAAA-MM-JJ |
| Diffusion | <application + audiences> |
| Export des données sous-jacentes | <autorisé / désactivé> |
| Permission Build | <groupes concernés, ou aucun> |

## Rôles d'espace de travail

| Environnement | Admin | Membre | Contributeur | Lecteur |
|---|---|---|---|---|
| Développement | <groupe> | <groupe> | <groupe> | — |
| Production | <groupe> | <groupe> | — | — |

## Matrice rôle × périmètre

| Rôle | Type | Table filtrée | Périmètre vu | Groupe(s) rattaché(s) | Validé par (fonction) | Testé le | Résultat |
|---|---|---|---|---|---|---|---|
| RLS_Region | RLS dynamique | Dim_Magasin | Régions de l'utilisateur selon la table de sécurité | <groupe> | <fonction> | AAAA-MM-JJ | conforme |
| RLS_Direction | RLS statique | — | Tout | <groupe> | <fonction> | AAAA-MM-JJ | conforme |

Utilisateur rattaché à aucun rôle : ne voit rien — testé le AAAA-MM-JJ.

## Objets masqués (OLS)

| Rôle | Table / colonne masquée | Raison | Visuels ou mesures concernés |
|---|---|---|---|
| — | — | — | — |

## Table de sécurité

| Élément | Valeur |
|---|---|
| Table | <ex. Dim_Utilisateur> |
| Source | <référentiel d'où viennent les droits> |
| Responsable de la mise à jour (fonction) | <fonction> |
| Fréquence d'actualisation | <quotidienne / …> |

## Données sensibles

| Colonne ou table | Nature | Mesure prise |
|---|---|---|
| <table[colonne]> | <personnelle / santé / financière> | <non chargée / pseudonymisée / OLS / agrégée> |

## Historique

| Date | Changement | Demandé par (fonction) | Test |
|---|---|---|---|
| AAAA-MM-JJ | Création de RLS_Region | <fonction> | T-0xx conforme |
```

Règles de tenue :

- Mettre à jour le fichier **dans le même commit** que le changement de rôle.
- La colonne « Testé le » renvoie aux cas de `tests/ACCEPTANCE.md` (`powerbi-testing`).
- Un écart connu et accepté (rôle non testé, donnée sensible encore chargée) va aussi dans `DEBT.md` (`powerbi-lean`).
