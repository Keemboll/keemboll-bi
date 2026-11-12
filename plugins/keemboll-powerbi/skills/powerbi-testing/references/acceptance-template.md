# Modèle de `tests/ACCEPTANCE.md`

Copier le bloc ci-dessous dans `tests/ACCEPTANCE.md`. **Aucune valeur réelle sensible** : la colonne « Résultat » contient *conforme*, *non conforme* ou *non exécuté* ; les chiffres restent hors dépôt. Les personnes sont désignées par leur **fonction**.

```markdown
# Recette — <nom du projet>

Version testée : <branche ou commit> — Environnement : <développement / test>
Période des données : <ex. jusqu'à fin 2026-10>

## Synthèse

| Niveau | Cas | Conformes | Non conformes | Non exécutés |
|---|---|---|---|---|
| 1 Intégrité | 4 | 4 | 0 | 0 |
| 2 Rapprochement | 2 | 2 | 0 | 0 |
| 3 Mesures | 6 | 5 | 1 | 0 |
| 4 Non-régression | 1 | 1 | 0 | 0 |
| 5 RLS | 4 | 4 | 0 | 0 |
| 6 Rapport | 5 | 5 | 0 | 0 |

## Cas

| Test | Niveau | Cas | Attendu | Résultat | Exécuté par | Date | Remarque |
|---|---|---|---|---|---|---|---|
| T-001 | 1 | Clés client uniques | Zéro ligne | conforme | utilisateur (DAX Studio) | AAAA-MM-JJ | |
| T-010 | 2 | CA mensuel = système source | Égalité à 0,01 près par mois | conforme | utilisateur | AAAA-MM-JJ | Source : extraction comptable |
| T-020 | 3 | CA HT N-1 sur la première année | Vide, sans erreur | non conforme | agent (avec accord) | AAAA-MM-JJ | Renvoie 0 → D-007 |
| T-050 | 5 | RLS_Region, profil une région | Une seule région visible | conforme | utilisateur (Afficher comme) | AAAA-MM-JJ | |
| T-051 | 5 | Utilisateur hors table de sécurité | Aucune ligne | conforme | utilisateur | AAAA-MM-JJ | |

## Écarts

| Test | Écart constaté (sans valeur) | Cause | Suite |
|---|---|---|---|
| T-020 | Zéro au lieu de vide | `COALESCE` en trop | Corrigé — M-012 / ou dette D-007, échéance AAAA-MM-JJ |

## Décision

| Élément | Valeur |
|---|---|
| Recette métier menée par (fonction) | <ex. Responsable contrôle de gestion> |
| Date | AAAA-MM-JJ |
| Décision | <accepté / accepté avec réserves / refusé> |
| Réserves | <D-xxx, D-yyy — ou aucune> |
| Mise en production autorisée | <oui / non> |
```

Règles de tenue :

- Une recette par version mise en production : conserver les précédentes dans l'historique Git plutôt que d'empiler les tableaux.
- *Non exécuté* est un résultat honnête ; il bloque la décision « accepté » pour les niveaux 1, 2 et 5 — **À ADAPTER**.
- Les identifiants `D-xxx` et `M-xxx` sont ceux de `DEBT.md` et `CHANGES.md` (`powerbi-lean`).
- Les dates des tests RLS sont reportées dans `SECURITY_MODEL.md` (`powerbi-governance`).
