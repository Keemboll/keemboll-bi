# Checklist — fusion et mise en production

Chaque ligne est **vérifiée**, pas supposée. Pour chaque case, noter la preuve (sortie de script, capture, nom du relecteur). Une case non vérifiable est signalée comme telle, jamais cochée par défaut.

## Avant de fusionner dans `main`

- [ ] La branche ne contient qu'**un changement cohérent** ; `git diff main...` relu en entier.
- [ ] Aucun fichier interdit dans le diff : `cache.abf`, `localSettings.json`, `.pbix`, extrait de données, secret, identifiant d'espace de travail.
- [ ] Revue `powerbi-lean` en mode `review` : verdict *prêt à commit*.
- [ ] Tests du changement passés ; valeurs avant / après comparées pour toute mesure modifiée (`powerbi-testing`).
- [ ] Renommage ou suppression : inventaire `lean.py usage` fait, visuels mis à jour, rapports connectés au modèle publié vérifiés.
- [ ] `CHANGES.md` : entrée `M-xxx` ; `DEBT.md` à jour ; `lean.py dette` sans incohérence.
- [ ] Le `.pbip` s'ouvre dans Power BI Desktop sans erreur après la dernière mise à jour depuis `main`.
- [ ] CI verte.
- [ ] Revue humaine approuvée.

## Avant la mise en production

### Qualité
- [ ] `lean.py audit` sur tout le projet : aucun constat de priorité 1 ; les constats restants sont corrigés ou consignés dans `DEBT.md`.
- [ ] Recette faite en environnement de test et **signée par le métier** (`powerbi-testing`).
- [ ] Performance : pages principales mesurées, aucune régression par rapport à la version en production (`powerbi-performance`).

### Sécurité et gouvernance (`powerbi-governance`)
- [ ] Rôles RLS / OLS testés avec au moins un utilisateur par rôle.
- [ ] Étiquette de sensibilité posée — **À ADAPTER**.
- [ ] Accès à l'espace de production et audience de l'application revus ; `SECURITY_MODEL.md` à jour.

### Documentation (`powerbi-documentation`)
- [ ] `DATA_DICTIONARY.md` régénéré depuis le modèle livré.
- [ ] Note de version rédigée à partir des entrées `M-xxx` depuis le tag précédent.
- [ ] `KPI.md` cohérent avec les mesures livrées (`powerbi-project`).

### Environnement
- [ ] Paramètres de source pointant vers la production (règles de déploiement ou paramétrage de l'espace cible) ; aucune source de dev ou de test restante.
- [ ] Actualisation planifiée, identifiants de la source et passerelle en place dans l'espace cible.
- [ ] Créneau de mise en production convenu ; utilisateurs prévenus si rupture.

### Retour arrière
- [ ] Tag de la version actuellement en production identifié.
- [ ] Procédure écrite dans la PR : qui décide, comment republier le tag précédent, combien de temps cela prend.
- [ ] Changement **non réversible** par simple republication (changement de grain, colonne supprimée à la source, historique d'actualisation incrémentielle) : signalé explicitement et accepté.

## Après la mise en production

- [ ] Tag annoté `vX.Y.Z` posé sur le commit publié (**À ADAPTER**).
- [ ] Première actualisation réussie ; pages principales ouvertes avec un compte utilisateur, pas un compte administrateur.
- [ ] Chiffres clés rapprochés de la source ou de la version précédente (`powerbi-testing`).
- [ ] Note de version diffusée ; branche fusionnée supprimée.

## Qui fait quoi

| Action | Agent | Humain |
|---|---|---|
| Lancer les scripts, relire le diff, préparer la description de PR et la note de version | oui | — |
| Cocher une case à partir d'une preuve produite | oui, en citant la preuve | — |
| Approuver la PR, signer la recette | non | oui |
| Fusionner, taguer, pousser, promouvoir | sur demande explicite, une action à la fois | oui |
| Écrire en production | **jamais directement** | par la voie de promotion |
