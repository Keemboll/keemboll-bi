# Modèle de HANDOVER.md

Dossier court pour la personne qui reprend le projet. Il **pointe** vers les autres fichiers au lieu de les recopier ; il ne contient que ce qui n'est écrit nulle part ailleurs.

```markdown
# Passation — <nom du projet> · <date>

## En une phrase
<À quoi sert ce projet et pour qui.>

## Où trouver quoi

| Sujet | Fichier |
|---|---|
| Besoin, périmètre, indicateurs | `SCOPE.md`, `KPI.md` |
| Modèle : tables, mesures, relations | `DATA_DICTIONARY.md` (régénéré le <date>) |
| Rapport : pages et public | `REPORT.md` |
| Sécurité et accès | `SECURITY_MODEL.md` |
| Tests et recette | `tests/`, `tests/ACCEPTANCE.md` |
| Ce qui reste à corriger | `DEBT.md` |
| Ce qui a été fait | `CHANGES.md`, `RELEASE_NOTES.md` |

## Sources et actualisation
- Sources : <systèmes, sans chaîne de connexion ni identifiant>
- Actualisation : <fréquence, qui est alerté en cas d'échec>
- Environnements et déploiement : voir `powerbi-alm` — <espaces de travail désignés par leur rôle : dev / test / prod>

## Ce qu'il faut savoir avant de toucher au modèle
- <choix de modélisation non évident et sa raison>
- <mesure sensible : définition arbitrée avec le métier, ne pas la modifier sans lui>
- <piège connu : objet utilisé par un autre rapport, renommage risqué>

## En cours et prochaines étapes
- <travail commencé, branche, état>
- <dettes prioritaires>

## Contacts
- Propriétaire métier : <fonction> · Responsable technique : <fonction> · Accès : <à qui demander>
```

## Règles

- Régénérer `DATA_DICTIONARY.md` et lancer `lean.py dette` **avant** d'écrire la passation : elle cite leur état du jour.
- La section « Ce qu'il faut savoir » se remplit avec l'utilisateur : ce sont les décisions et les pièges que ni le modèle ni Git ne racontent. Ne pas la remplir par déduction.
- Fonctions plutôt que noms de personnes ; aucun identifiant de tenant ou d'espace de travail, aucun secret, aucune valeur réelle.
- Une section vide se supprime ou porte « rien à signaler » : pas de remplissage.
