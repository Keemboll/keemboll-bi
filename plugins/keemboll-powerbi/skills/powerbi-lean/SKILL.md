---
name: powerbi-lean
description: "Sobriété et revue des modèles et rapports Power BI : moins d'objets, pas moins de documentation. Trois modes : review (revue du git diff d'un projet PBIP), audit (mesures et colonnes inutilisées, doublons DAX, valeurs en dur, FILTER sur table entière, summarizeBy, clés visibles, table de dates) et dette (registre DEBT.md des raccourcis assumés et journal CHANGES.md qui se remplit à mesure que la dette diminue). Inclut un script Python en lecture seule (lean.py) qui inventorie aussi les champs utilisés par le rapport avant un renommage. Triggers: revue, review, audit, journal des modifications, changelog, solder une dette, progression de la dette, nettoyage, simplifier, inutilisé, unused, doublon, duplicate, dette technique, tech debt, refactoriser, avant renommage, où est utilisée cette mesure, impact."
---

# powerbi-lean — moins d'objets, pas moins de documentation

But : chaque mesure, colonne ou table doit **servir une question** du rapport. On retire le superflu (doublons, objets morts, valeurs en dur, logique recopiée) ; on **ne retire jamais** descriptions, commentaires QUOI / COMMENT / ADAPTER, dossiers d'affichage ni formats.

Applique `powerbi-conventions` (validation, Git, modèle existant, confidentialité), `powerbi-performance` (réécritures DAX) et `powerbi-dax-library` (motifs de remplacement). **Lecture seule par défaut** : aucun changement sans plan validé.

## Le script

`scripts/lean.py` (dans le dossier de ce skill, Python 3.8+, bibliothèque standard uniquement) analyse un projet PBIP **sans rien modifier** : TMDL du modèle + PBIR du rapport.

```bash
python "<dossier du skill>/scripts/lean.py" audit "<dossier du projet PBIP>"            # audit complet
python "<dossier du skill>/scripts/lean.py" audit "<dossier>" --changed                  # fichiers modifiés depuis le dernier commit
python "<dossier du skill>/scripts/lean.py" usage "<dossier>"                            # champs utilisés par page / visuel
python "<dossier du skill>/scripts/lean.py" usage "<dossier>" --field "'Table'[Colonne]" # où un champ est utilisé
python "<dossier du skill>/scripts/lean.py" usage "<dossier>" --field "[Mesure]"
python "<dossier du skill>/scripts/lean.py" dette "<dossier>"                            # état DEBT.md + CHANGES.md
python "<dossier du skill>/scripts/lean.py" catalogue "<dossier>"                        # dictionnaire de données (Markdown, voir powerbi-documentation)
```

Ajouter `--json` pour une sortie exploitable. Sous Windows, utiliser `python` (ou `py`) ; ailleurs `python3`. Le dossier peut être celui du `.pbip`, du `*.SemanticModel` ou le fichier `.pbip`. Ce que le script vérifie et ses limites : [references/audit-rules.md](references/audit-rules.md).

Toujours **exécuter le script** plutôt que deviner l'utilisation d'un champ : c'est lui qui fait foi pour « utilisé / inutilisé ».

## Mode `review` — revue d'un changement

Quand : après une modification du modèle ou du rapport, avant le commit.

1. `git status` et `git diff` dans le dossier du projet (TMDL et PBIR).
2. `lean.py audit <dossier> --changed` : constats limités aux fichiers modifiés.
3. Relire le diff avec la grille [references/review-grid.md](references/review-grid.md) : logique dupliquée, mesure qui réécrit une mesure existante, valeur en dur, documentation retirée, renommage sans mise à jour des visuels, `lineageTag` copié.
4. Rendre **au plus 7 constats**, classés par impact : objet, problème, correction proposée (avec DAX si utile). Terminer par un verdict : *prêt à commit* / *à corriger*.
5. Ne rien modifier sans accord.

## Mode `audit` — revue de tout le projet

Quand : prise en main d'un modèle, avant une refonte, avant publication.

1. `lean.py audit <dossier>` (+ `usage` si des renommages sont envisagés).
2. Compléter par la lecture ciblée de ce que le script ne voit pas : logique quasi dupliquée (mêmes calculs avec variations), mesures « fourre-tout » (SWITCH qui recopie d'autres mesures), noms trompeurs.
3. Restituer un tableau **priorisé gain / risque** :
   - **Sans impact visuel** d'abord : table de dates, `summarizeBy`, masquage des clés, formats, descriptions.
   - **Nettoyage** : suppression d'objets inutilisés (après confirmation qu'aucun autre rapport connecté ne les utilise), fusion des doublons.
   - **Refactorisation** : mesures recopiées → composition de mesures de base ; valeurs en dur → mesures ou tables de référence.
   - **Renommages** en dernier, avec l'inventaire `usage` de chaque objet.
4. Proposer de consigner dans `DEBT.md` ce qui ne sera pas corrigé tout de suite.

## Mode `dette` — registre des raccourcis et journal des modifications

Deux fichiers à la racine du projet, à côté du `.pbip`, versionnés avec lui — **jamais en commentaire dans le modèle publié** :

| Fichier | Rôle | Modèle |
|---|---|---|
| `DEBT.md` | Ce qui reste à corriger (raccourcis assumés, constats d'audit non traités) | [debt-template.md](references/debt-template.md) |
| `CHANGES.md` | Ce qui a été corrigé ou ajouté, plus récent en haut ; se remplit à mesure que la dette diminue | [changes-template.md](references/changes-template.md) |

- **État** : `python "<dossier du skill>/scripts/lean.py" dette "<dossier du projet>"` → dettes ouvertes / soldées, progression, priorités, échéances dépassées, prochains identifiants (D-xxx, M-xxx) et incohérences entre les deux fichiers.
- **Ajouter une dette** : nouvelle entrée `D-xxx` dans « Ouvert » ; à la fin d'un `audit`, proposer d'y consigner les constats non traités.
- **Solder une dette** (après correction **et** vérification) :
  1. ajouter en haut de `CHANGES.md` une entrée `M-xxx` : dette(s) soldée(s), type, objets modifiés, avant → après, impact sur le rapport, vérification (sans valeurs réelles) ;
  2. déplacer l'entrée `D-xxx` de « Ouvert » vers « Soldé » avec `**Soldé le**` et `**Modification** : M-xxx` ;
  3. relancer `lean.py dette` : aucune incohérence attendue ;
  4. un seul commit pour le changement et les deux fichiers, message `M-xxx: <résumé>`.
- **Évolution hors dette** (nouvelle page, nouvelle mesure) : entrée `M-xxx` avec `**Dette** : hors dette`.
- **Avancée partielle** : `**Dette** : D-xxx (partielle)`, la dette reste ouverte.
- **Projet qui a déjà une dette mais pas de journal** : reconstituer `CHANGES.md` depuis `git log` et `DEBT.md`, sans rien inventer — procédure dans [changes-template.md](references/changes-template.md#initialiser-le-journal-sur-un-projet-qui-a-déjà-une-dette).
- Ne jamais solder une dette sans entrée de journal, ni écrire une entrée de journal sans avoir vérifié les valeurs.

## Règles

- Supprimer ou fusionner seulement après inventaire `usage` **et** validation explicite.
- « Inutilisé » = non référencé par **ce** rapport : un autre rapport connecté au modèle publié peut l'utiliser. Le dire à chaque fois.
- Une simplification qui change un résultat n'est pas une simplification : vérifier les valeurs avant/après (requête DAX de contrôle).
- Jamais de commentaire `TODO` / `shortcut` dans les mesures : la dette va dans `DEBT.md`.
