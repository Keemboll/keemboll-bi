# `.gitignore` for a PBIP project

Place it at the repository root **before the first commit**.

```gitignore
# Power BI — local settings and loaded data (NEVER version these)
**/.pbi/localSettings.json
**/.pbi/cache.abf

# Power BI binary files: the project is versioned as PBIP, not PBIX
*.pbix
*.pbit

# Data exports and extracts
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

# Python (skill scripts)
__pycache__/
*.pyc

# OS / editors
.DS_Store
Thumbs.db
.vscode/
.idea/
```

## Why

| Entry | Reason |
|---|---|
| `**/.pbi/cache.abf` | Local copy of the **data loaded** into the model. Versioning it amounts to publishing the data. |
| `**/.pbi/localSettings.json` | Settings specific to the workstation and the user; a pointless source of conflicts. |
| `*.pbix`, `*.pbit` | Binaries: no diff, no merge; a `.pbix` carries the data. |
| `*.csv`, `*.xlsx`, `*.parquet` | Data extracts, ignored by default. For a small reference file versioned on purpose and free of personal data, add an exception `!path/file.csv`. |
| Secrets | No token, certificate or password in the repository, even a private one. |

## Checks

- Before the first commit: `git status --ignored` must list `cache.abf` and `localSettings.json` among the ignored files.
- If `cache.abf` or a `.pbix` has **already** been committed: adding it to `.gitignore` does not remove it from the history. Tell the user; `git rm --cached` removes it from future commits, but purging the history is a rewrite the agent does not do on its own.
- Keep **everything else** in `*.SemanticModel/` and `*.Report/` versioned, including `.platform`, `definition.pbism` and `definition.pbir`.
- Line endings: let Git normalise (`* text=auto` in `.gitattributes`) to avoid whole-file diffs between workstations.
