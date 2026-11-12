# Modèle de RELEASE_NOTES.md

Note destinée aux **utilisateurs du rapport**, rédigée à chaque publication. Elle se construit à partir des entrées `M-xxx` de `CHANGES.md` (skill `powerbi-lean`) ajoutées depuis la publication précédente : le journal est technique, la note dit ce qui change pour le lecteur. Plus récent en haut.

```markdown
# Notes de version — <nom du rapport>

## <version ou date de publication> · 2026-11-15

### Nouveau
- Page « Détail clients » : suivi des clients par segment. (M-014)

### Modifié
- `Marge brute %` exclut désormais les avoirs : les valeurs antérieures peuvent différer. (M-012)

### Corrigé
- Le cumul annuel s'arrêtait au dernier mois complet. (M-013)

### À savoir
- <limite connue, indicateur provisoire, action attendue de l'utilisateur>
```

## Procédure

1. Lister les entrées `M-xxx` depuis la dernière publication (date ou étiquette Git, voir `powerbi-alm`).
2. Écarter celles sans effet pour le lecteur (refactorisation, masquage, descriptions) : elles restent dans le journal.
3. Reformuler chaque entrée retenue en **effet visible** : quelle page, quel indicateur, ce qui change dans la lecture.
4. Signaler explicitement tout **changement de définition** d'un indicateur : c'est l'information la plus importante de la note.
5. Citer l'identifiant `M-xxx` pour la traçabilité.

## Règles

- Rien dans la note qui ne soit dans `CHANGES.md` : si une évolution n'y figure pas, compléter d'abord le journal.
- Pas de valeurs réelles ; décrire le sens du changement, pas les montants.
- Numérotation des versions : celle des tags de `powerbi-alm` (`vX.Y.Z` — **À ADAPTER**), suivie de la date de publication.
