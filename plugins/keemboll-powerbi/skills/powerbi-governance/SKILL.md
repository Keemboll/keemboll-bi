---
name: powerbi-governance
description: "Sécurité et gouvernance d'un modèle sémantique ou d'un rapport Power BI : sécurité au niveau des lignes (RLS statique et dynamique), sécurité au niveau des objets (OLS), étiquettes de sensibilité, endossement (promu / certifié), propriété du modèle, rôles d'espace de travail, partage par application, permission Build, données personnelles ou de santé, et fiche SECURITY_MODEL.md du projet. À utiliser pour concevoir, relire ou modifier des rôles de sécurité, décider qui voit quoi, préparer une publication ou auditer les accès d'un projet. Triggers: sécurité, security, gouvernance, governance, RLS, row-level security, OLS, object-level security, rôle, role, USERPRINCIPALNAME, étiquette de sensibilité, sensitivity label, certifié, certified, endossement, endorsement, espace de travail, workspace, partage, sharing, application, app, permission Build, accès, données personnelles, RGPD, GDPR, moindre privilège."
---

# Gouvernance et sécurité Power BI

But : savoir **qui voit quoi**, l'écrire, le tester, et ne publier que ce qui est autorisé.

Ce skill fait foi pour la **conception** de la sécurité. Font foi ailleurs :

- `powerbi-conventions` : nommage des rôles (`RLS_<périmètre>`), confidentialité des métadonnées lues par un agent, processus de validation avant modification.
- `powerbi-testing` : protocole de test des rôles (niveau 5) et procès-verbal de recette.
- `powerbi-tmdl` : syntaxe et édition des fichiers de rôles.
- `powerbi-alm` : environnements et déploiement ; `powerbi-project` : phases et livrables.
- La **mécanique** (attribuer des membres à un rôle, poser une étiquette, régler les accès d'un espace de travail) relève des skills Microsoft s'ils sont installés (`semantic-model-authoring`, `onelake-catalog-cli`), sinon du portail Power BI / Fabric.

## Règles

1. **Toute création, modification ou suppression de rôle** = plan écrit → **validation explicite** de l'utilisateur → exécution → test (`powerbi-testing`) → mise à jour de `SECURITY_MODEL.md`. Jamais « au passage » d'une autre tâche.
2. La RLS **ne protège que les lecteurs** : dans le service, les rôles Admin, Membre et Contributeur de l'espace de travail voient toutes les données du modèle. La sécurité commence donc par les rôles d'espace de travail.
3. Filtrer les **dimensions**, jamais les faits (règle de `powerbi-conventions`) ; ici : laisser les relations propager le filtre.
4. **Jamais d'e-mail, de nom de personne ni d'identifiant** en dur dans une expression de rôle, ni dans `SECURITY_MODEL.md` : les personnes sont rattachées à des **groupes de sécurité** dans le service, pas dans les fichiers versionnés.
5. Un utilisateur membre de **plusieurs rôles** voit l'**union** de leurs périmètres : un rôle ne peut pas en restreindre un autre. Exception : RLS et OLS portées par des rôles différents ne se combinent pas (erreur) — voir OLS.
6. Pas de publication sans propriétaire identifié — **À ADAPTER** ; étiquette de sensibilité : règle de `powerbi-conventions`.
7. L'agent **n'attribue pas** de membres, ne partage pas et ne change pas d'étiquette sans demande explicite : ce sont des actions visibles par d'autres personnes.

## RLS — sécurité au niveau des lignes

| Besoin | Approche |
|---|---|
| Quelques périmètres fixes et stables (2 à 5 régions — **À ADAPTER**) | **Statique** : un rôle par périmètre, filtre en dur sur la dimension |
| Périmètres nombreux ou changeants, un utilisateur = un ou plusieurs périmètres | **Dynamique** : un seul rôle, table de sécurité + `USERPRINCIPALNAME()` |
| Hiérarchie (un responsable voit son équipe) | Dynamique + fonctions `PATH` sur la dimension hiérarchique |

- **Dynamique** : une table de sécurité (utilisateur × périmètre), **masquée**, alimentée depuis une source maîtrisée (annuaire, référentiel RH) — pas saisie à la main dans le modèle. Elle est elle-même filtrée par le rôle, pour qu'un utilisateur ne lise pas les droits des autres.
- **Propagation** : le filtre suit les relations dans le sens un → plusieurs. Une relation bidirectionnelle ne propage la sécurité dans l'autre sens que si l'option *Appliquer le filtre de sécurité dans les deux directions* est cochée ; préférer filtrer directement la bonne dimension.
- **Plusieurs-à-plusieurs** : passer par une table pont (`powerbi-data-modeling`) et vérifier par test que le filtre atteint bien les faits.
- **Tout le monde / personne** : prévoir explicitement le cas de l'utilisateur absent de la table de sécurité (il ne doit rien voir) et, si nécessaire, un rôle « tout voir » distinct plutôt qu'une exception dans la formule.
- **DirectQuery / Direct Lake** : la RLS du modèle s'applique, mais les règles posées côté source (entrepôt, point de terminaison SQL) ont leurs propres effets — notamment un repli possible en DirectQuery pour Direct Lake sur point de terminaison SQL. Vérifier le comportement dans la documentation Microsoft en vigueur avant de s'engager.
- **Performance** : une expression de rôle est évaluée à chaque requête ; la garder simple (pas d'itérateur sur une grande table), voir `powerbi-performance`.

Exemples TMDL et DAX, pièges détaillés : [references/rls-ols.md](references/rls-ols.md).

## OLS — sécurité au niveau des objets

Masque **une table ou une colonne entière** (salaire, coût, donnée nominative) à un rôle : pour ce rôle, l'objet n'existe pas.

- À réserver aux colonnes réellement sensibles : un visuel ou une mesure qui dépend d'un objet masqué **tombe en erreur** pour ce rôle. Inventorier les usages avant (`powerbi-lean`, commande `usage`).
- Se définit dans la vue TMDL de Power BI Desktop (script `createOrReplace` du rôle) ou avec un outil externe (Tabular Editor) ; la fenêtre « Gérer les rôles » ne la propose pas — à vérifier sur la version en cours.
- Combiner RLS et OLS dans **le même rôle** : un utilisateur membre d'un rôle portant la RLS et d'un autre portant l'OLS reçoit une **erreur à l'exécution des requêtes** (restriction documentée par Microsoft).
- Masquer une colonne (`isHidden`) **n'est pas** de la sécurité : elle reste interrogeable.
- Solution souvent plus simple : ne pas charger la colonne sensible, ou la placer dans un modèle séparé à accès restreint.

## Accès, partage et endossement

| Sujet | Règle par défaut — **À ADAPTER** |
|---|---|
| Rôles d'espace de travail | **Moindre privilège** : Admin = 2 propriétaires au plus ; Membre / Contributeur = équipe BI seulement ; les consommateurs ne sont **pas** ajoutés à l'espace de travail |
| Diffusion | Par **application** (audiences), pas par partage direct de rapports ni accès Lecteur à l'espace de travail |
| Groupes | Accès donnés à des **groupes de sécurité**, jamais à des personnes une par une |
| Permission **Build** | Accordée seulement à ceux qui doivent créer leurs propres rapports ou analyser dans Excel sur le modèle ; elle donne accès à tout le modèle (dans la limite de la RLS / OLS) |
| Propriété | Chaque modèle a un **propriétaire métier** et un **propriétaire technique** nommés dans `SECURITY_MODEL.md` par leur fonction ; pas de modèle rattaché à un compte personnel qui peut disparaître |
| Endossement | **Promu** : jugé fiable par son propriétaire. **Certifié** : validé selon le processus de l'organisation, par les personnes habilitées par l'administrateur. Ne certifier qu'après recette signée (`powerbi-testing`) |
| Étiquette de sensibilité | Posée sur le modèle et le rapport avant publication ; elle suit le contenu (héritage en aval, exports) selon la configuration du tenant |
| Export des données | Décider par rapport si l'export des données sous-jacentes est permis ; le désactiver pour les données sensibles |

## Données personnelles et de santé

- **Minimiser** : ne charger que les colonnes nécessaires aux questions du rapport. Pas de nom, téléphone, adresse ou identifiant national « au cas où ».
- Préférer des **agrégats** ou des identifiants pseudonymisés ; attention aux petits effectifs qui permettent de ré-identifier (seuil d'affichage — **À ADAPTER**).
- Signaler à l'utilisateur toute donnée nominative trouvée dans le modèle, **sans la recopier** dans la réponse, `DEBT.md` ou `SECURITY_MODEL.md`.
- Confidentialité de ce que l'agent lit lui-même : voir `powerbi-conventions` (confidentialité des métadonnées).

## Livrable : `SECURITY_MODEL.md`

À la racine du projet, à côté du `.pbip`, versionné : matrice rôle × périmètre, groupes rattachés (par nom de groupe), propriétaires (par fonction), étiquette, endossement, date et résultat du dernier test. **Aucun nom de personne, aucun e-mail, aucune valeur de donnée.** Modèle : [references/security-template.md](references/security-template.md).

## Processus

1. **Inventorier** : rôles existants (dossier `definition/roles/` du modèle), tables de sécurité, relations bidirectionnelles, colonnes sensibles, `SECURITY_MODEL.md` s'il existe.
2. **Recueillir le besoin** : qui (profils, pas personnes) doit voir quoi ; qui valide ; quelles données sont sensibles.
3. **Proposer un plan** : rôles créés / modifiés / supprimés, expressions DAX, impact sur les visuels (OLS), tests prévus.
4. **Attendre la validation explicite.**
5. **Exécuter** (`powerbi-tmdl` pour les fichiers), sur une branche de développement (`powerbi-alm`).
6. **Tester** chaque rôle selon `powerbi-testing` ; si aucun moteur n'est disponible, fournir les requêtes et le dire.
7. **Mettre à jour `SECURITY_MODEL.md`** et résumer : rôle / action / périmètre / test.

## Avant publication — contrôle rapide

- [ ] Chaque rôle est testé, y compris l'utilisateur sans droit.
- [ ] Aucun e-mail ni nom en dur dans les rôles, paramètres ou expressions M.
- [ ] Les consommateurs passent par l'application, pas par l'espace de travail.
- [ ] Étiquette de sensibilité et propriétaires renseignés.
- [ ] `SECURITY_MODEL.md` à jour.
