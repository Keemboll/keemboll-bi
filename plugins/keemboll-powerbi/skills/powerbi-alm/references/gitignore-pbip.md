# `.gitignore` d'un projet PBIP

À placer à la racine du dépôt **avant le premier commit**.

```gitignore
# Power BI — réglages locaux et données chargées (ne JAMAIS versionner)
**/.pbi/localSettings.json
**/.pbi/cache.abf

# Fichiers binaires Power BI : le projet se versionne en PBIP, pas en PBIX
*.pbix
*.pbit

# Exports et extraits de données
*.csv
*.xlsx
*.parquet
exports/

# Secrets
.env
.env.*
*.pem
*.key
*.pfx

# Python (scripts des skills)
__pycache__/
*.pyc

# OS / éditeurs
.DS_Store
Thumbs.db
.vscode/
.idea/
```

## Pourquoi

| Entrée | Raison |
|---|---|
| `**/.pbi/cache.abf` | Copie locale des **données chargées** dans le modèle. La versionner revient à publier les données. |
| `**/.pbi/localSettings.json` | Réglages propres au poste et à l'utilisateur ; source de conflits sans intérêt. |
| `*.pbix`, `*.pbit` | Binaires : pas de diff, pas de fusion ; un `.pbix` embarque les données. |
| `*.csv`, `*.xlsx`, `*.parquet` | Extraits de données. **À ADAPTER** : retirer la ligne pour un petit fichier de référence volontairement versionné et sans donnée personnelle (ajouter alors une exception `!chemin/fichier.csv`). |
| Secrets | Aucun jeton, certificat ou mot de passe dans le dépôt, même privé. |

## Vérifications

- Avant le premier commit : `git status --ignored` doit lister `cache.abf` et `localSettings.json` parmi les fichiers ignorés.
- Si `cache.abf` ou un `.pbix` a **déjà** été commité : l'ajouter au `.gitignore` ne le retire pas de l'historique. Le signaler à l'utilisateur ; `git rm --cached` le retire des commits futurs, mais purger l'historique est une réécriture que l'agent ne fait pas de lui-même.
- Garder **tout le reste** de `*.SemanticModel/` et `*.Report/` versionné, y compris `.platform`, `definition.pbism` et `definition.pbir`.
- Fin de ligne : laisser Git normaliser (`* text=auto` dans `.gitattributes`) pour éviter les diffs entiers entre postes.
