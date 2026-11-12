# Modèle de REPORT.md

Fiche du rapport, à la racine du projet. Elle décrit **à qui sert le rapport et à quelle question répond chaque page** ; les champs utilisés par visuel se retrouvent avec `lean.py usage` et ne sont pas recopiés ici.

```markdown
# Fiche du rapport — <nom du rapport>

- **Modèle sémantique** : <nom> (voir `DATA_DICTIONARY.md`)
- **Public** : <rôles ou équipes, pas de noms de personnes>
- **Décisions éclairées** : <ce que le lecteur fait après avoir lu le rapport>
- **Fréquence de consultation** : <quotidienne / hebdomadaire / mensuelle>
- **Actualisation des données** : <fréquence et heure> — À ADAPTER
- **Propriétaire métier** : <fonction> · **Responsable technique** : <fonction>
- **Sécurité** : voir `SECURITY_MODEL.md`

## Pages

| # | Page | Question à laquelle elle répond | Indicateurs principaux | Filtres et segments |
|---|---|---|---|---|
| 1 | Synthèse | Où en sommes-nous par rapport à l'objectif ? | `CA HT`, `Marge brute %` | Année, Région |
| 2 | Détail clients | Quels clients expliquent l'écart ? | `Nb clients`, `CA HT` | Année, Segment |

## Navigation et interactions

- Extraction (drill-through) : <page source → page cible, champ>
- Infobulles de rapport : <page d'infobulle → visuels concernés>
- Signets et interrupteurs : <ex. Plan / N-1>

## Limites connues

- <périmètre exclu, données disponibles à partir de quelle date, décalage d'actualisation>
- <indicateur non comparable avant une date donnée>
- Dette ouverte : voir `DEBT.md`
```

## Règles

- Une page sans question claire est un constat à remonter, pas une ligne à remplir par défaut (voir les quatre questions de `powerbi-report-design`).
- Les noms d'indicateurs sont ceux du modèle, entre accents graves.
- Les limites connues se rédigent pour un lecteur métier : ce qu'il ne doit **pas** conclure du rapport.
- Aucune valeur réelle ni capture avec des données réelles.
