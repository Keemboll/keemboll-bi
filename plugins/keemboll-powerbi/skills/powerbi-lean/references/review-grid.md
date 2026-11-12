# Grille de revue d'un diff PBIP

| # | Question | Où regarder |
|---|---|---|
| 1 | Une nouvelle mesure recalcule-t-elle ce qu'une mesure existante fait déjà ? | `tables/*.tmdl` : chercher le même agrégat / la même colonne |
| 2 | Une mesure recopie-t-elle la logique d'autres mesures au lieu de les référencer ? | SWITCH, IF à rallonge |
| 3 | Valeurs en dur ajoutées (dates, identifiants, libellés de données) ? | DAX, partitions M |
| 4 | Documentation retirée ou absente (description `///`, commentaire QUOI/COMMENT/ADAPTER, format, dossier) ? | lignes supprimées du diff |
| 5 | Renommage : toutes les références mises à jour (DAX, `*.Report/`, relations, tri, rôles, cultures) ? | `lean.py usage --field` sur l'ancien nom |
| 6 | Relation ajoutée ou modifiée : sens, cardinalité, bidirectionnel justifié ? | `relationships.tmdl` |
| 7 | `lineageTag` dupliqué (copier-coller d'objet) ? | nouvelles lignes `lineageTag` |
| 8 | Objets créés puis jamais utilisés ? | `lean.py audit --changed` |
| 9 | Visuels : champs liés existants, titres-questions, couleurs du thème ? | `visual.json` modifiés |
| 10 | Secrets, e-mails ou noms de personnes ajoutés (rôles, paramètres) ? | `roles/`, `expressions.tmdl` |
