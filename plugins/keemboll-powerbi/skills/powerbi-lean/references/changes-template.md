# Modèle de CHANGES.md

Journal des modifications du projet, à la racine (à côté du `.pbip` et de `DEBT.md`), versionné avec le projet. **Plus récent en haut.** Il se remplit à mesure que la dette diminue : chaque dette soldée y a son entrée ; les évolutions hors dette (nouvelle page, nouvelle mesure) y sont aussi consignées.

```markdown
# Journal des modifications — <nom du projet>

## M-002 · 2026-10-20 · Fusion des mesures en doublon
- **Dette** : D-001 (soldée)
- **Type** : refactorisation
- **Objets modifiés** : `Mesures[012.Attendus]` réécrite pour référencer `[011.Approvisionne]`
- **Avant → après** : deux expressions DAX identiques → une mesure de base + une référence
- **Impact rapport** : aucun visuel modifié (vérifié avec `lean.py usage`)
- **Vérification** : valeurs comparées avant/après sur 3 périodes et 2 réseaux : identiques
- **Commit** : message `M-002: …` · **Par** : <nom>

## M-001 · 2026-10-15 · Table de dates marquée
- **Dette** : D-006 (soldée)
- **Type** : correction
- **Objets modifiés** : `Calendar` (dataCategory: Time, isKey sur DateValue)
- **Avant → après** : table non marquée → table de dates officielle
- **Impact rapport** : mesures `Cumul …` revérifiées
- **Vérification** : totaux mensuels identiques ; cumuls identiques
- **Commit** : message `M-001: …` · **Par** : <nom>
```

## Règles

- Identifiants **M-001, M-002…** jamais réutilisés. `python lean.py dette <projet>` donne le prochain.
- **Dette** : un ou plusieurs `D-xxx`, ou « hors dette ». `D-xxx (partielle)` (ou `(en cours)`) pour une avancée qui ne solde pas encore la dette : elle reste alors dans « Ouvert ». Une dette citée ici doit être déplacée dans « Soldé » de `DEBT.md` avec `**Modification** : M-xxx`.
- **Type** : correction · refactorisation · nettoyage · performance · nouvelle fonctionnalité · documentation.
- **Vérification** : décrire ce qui a été comparé et le verdict (identique / écart expliqué). **Ne jamais recopier de valeurs réelles** (chiffres d'indicateurs, noms de patients ou d'institutions si sensibles).
- **Commit** : le message de commit commence par l'identifiant (`M-002: fusion des doublons`) ; `git log --grep "M-002"` retrouve le commit sans avoir à recopier son hash.
- Une modification = un commit qui contient le changement du modèle/rapport **et** les mises à jour de `DEBT.md` et `CHANGES.md`.

## Initialiser le journal sur un projet qui a déjà une dette

1. **Ne rien inventer** : reconstituer uniquement à partir de `git log` / `git show` (depuis la création de `DEBT.md`) et de ce que `DEBT.md` mentionne déjà comme fait.
2. En-tête du fichier : *« Journal démarré le AAAA-MM-JJ ; les entrées antérieures sont reconstituées depuis l'historique Git. »*
3. Une entrée `M-xxx` par changement passé, **numérotées dans l'ordre chronologique** (M-001 = le plus ancien) mais **affichées du plus récent au plus ancien**. Pour ces entrées :
   - **Commit** : le hash court réel (`abc1234`), puisque le commit existe ;
   - **Vérification** : ce qui est connu, sinon « non vérifiée a posteriori » — ne pas affirmer une vérification qui n'a pas eu lieu.
4. Dette **entièrement** corrigée par le passé → la déplacer dans « Soldé » de `DEBT.md` (`**Soldé le**` = date du commit, `**Modification** : M-xxx`). Dette **partiellement** traitée → la laisser ouverte et citer `D-xxx (partielle)`.
5. Les changements antérieurs à la création de `DEBT.md` (commit initial, mise sous Git) : une seule entrée « hors dette » de type « documentation » suffit.
6. Terminer par `python lean.py dette <projet>` : zéro incohérence attendue.
7. Commit unique : `M-000: initialisation du journal des modifications` n'est pas une modification du modèle ; utiliser plutôt le message `docs: initialisation de CHANGES.md (reprise de l'historique)`.
