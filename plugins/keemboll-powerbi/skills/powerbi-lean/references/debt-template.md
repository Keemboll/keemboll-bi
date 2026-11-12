# Modèle de DEBT.md

À placer à la racine du projet, à côté du `.pbip`. Versionné avec le projet.

```markdown
# Dette technique — <nom du projet>

## Ouvert

### D-001 · Valeur en dur dans [Taux de suppression]
- **Objet** : `Mesures[Taux de suppression]`
- **Raccourci** : identifiant d'indicateur `= 16` codé en dur.
- **Pourquoi** : table de référence des indicateurs pas encore disponible.
- **Correction prévue** : relier `Indicateurs` et filtrer par code.
- **Priorité** : moyenne · **Échéance** : 2026-12-31
- **Ajouté le** : 2026-10-13 · **Par** : <nom>

## Soldé

### D-000 · Exemple soldé
- **Soldé le** : 2026-10-20 · **Modification** : M-001
```

Règles : un identifiant par entrée (D-001…, prochain numéro donné par `python lean.py dette <projet>`), une ligne « pourquoi » obligatoire, une échéance réaliste. Une entrée soldée renvoie toujours à son entrée de `CHANGES.md` ([modèle](changes-template.md)). Ne jamais recopier de données (valeurs patients, noms) dans ce fichier.
