# Continuous integration — examples

The CI analyses **the files of the repository** with `lean.py` (`powerbi-lean` skill). It connects to no workspace, reads no data and needs no secret.

## What `lean.py` returns

| Command | Exit code | Output |
|---|---|---|
| `audit <project> [--json]` | **0**, whether there are findings or not | `--json`: `{"findings": [{"prio", "cat", "obj", "detail", "file"}], "stats": {…}}` — `prio` is 1, 2 or 3 |
| `debt <project> [--json]` | **0**, whether there are inconsistencies or not | `--json`: `open`, `closed`, `progress`, `openItems`, `issues` (list of strings) … |
| unknown subcommand | **1** | help on standard output |
| `audit`: no `*.SemanticModel` folder, missing folder, read error | **1** | message on standard error |
| `debt`: `DEBT.md` and `CHANGES.md` missing, or wrong folder | **0**, `total: 0`, `issues: []` | the gate passes on nothing — check `PROJECT` |

Consequence: **the script never fails the build because of a finding**. There is no threshold option, and an unknown option is ignored without error. A CI step reads the JSON and decides. The small script below (`ci_threshold.py`, to place in the project repository, e.g. in `tests/`) applies the default threshold: fail on a priority 1 finding or a debt / change-log inconsistency.

```python
"""CI threshold: python ci_threshold.py audit.json debt.json"""
import json
import sys

audit = json.load(open(sys.argv[1], encoding="utf-8"))
debt = json.load(open(sys.argv[2], encoding="utf-8"))
blocking = [f for f in audit["findings"] if f["prio"] == 1]
for f in blocking:
    print(f"BLOCKING {f['cat']}: {f['obj']} - {f['detail']}")
for i in debt["issues"]:
    print(f"INCONSISTENCY {i}")
print(f"{len(audit['findings'])} finding(s), {len(blocking)} blocking; "
      f"{len(debt['issues'])} debt / change-log inconsistency(ies).")
sys.exit(1 if blocking or debt["issues"] else 0)
```

`debt` also reports **overdue items** in `issues`: with this threshold, a late debt blocks the PR. Filter those lines out in `ci_threshold.py` if that is not wanted.

## Making the script available

The CI has no access to the skills installed on a workstation. The script must be **in the project repository**: the skills installed in the project, e.g. `.agents/skills/powerbi-lean/`, versioned with it. Set the `LEAN` variable below to the folder actually used. Update that copy when the skill changes.

In the examples, `PROJECT` is the folder that contains the `.pbip` (`.` when it is at the root).

## GitHub Actions

`.github/workflows/powerbi-quality.yml`

```yaml
name: Power BI quality

on:
  pull_request:
    branches: [main]

permissions:
  contents: read

env:
  LEAN: .agents/skills/powerbi-lean/scripts/lean.py
  PROJECT: .

jobs:
  lean:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Audit (readable in the log)
        run: python "$LEAN" audit "$PROJECT"
      - name: Debt and change log
        run: python "$LEAN" debt "$PROJECT"
      - name: Threshold
        run: |
          python "$LEAN" audit "$PROJECT" --json > audit.json
          python "$LEAN" debt "$PROJECT" --json > debt.json
          python tests/ci_threshold.py audit.json debt.json
```

## Azure DevOps

`azure-pipelines.yml` — to run it on the PRs of an Azure Repos repository, add a **build validation policy** on the `main` branch (the YAML `pr:` triggers do not apply to Azure Repos).

```yaml
trigger: none

pool:
  vmImage: ubuntu-latest

variables:
  LEAN: .agents/skills/powerbi-lean/scripts/lean.py
  PROJECT: .

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: "3.12"
  - script: python "$(LEAN)" audit "$(PROJECT)"
    displayName: Audit (readable in the log)
  - script: python "$(LEAN)" debt "$(PROJECT)"
    displayName: Debt and change log
  - script: |
      python "$(LEAN)" audit "$(PROJECT)" --json > audit.json
      python "$(LEAN)" debt "$(PROJECT)" --json > debt.json
      python tests/ci_threshold.py audit.json debt.json
    displayName: Threshold
```

## Variants

- **Findings limited to the PR**: `audit --changed` compares the working tree to the last commit; in a CI the tree is clean, so the option returns nothing useful. To block only on the files of the PR, filter in `ci_threshold.py` the findings whose `file` (an **absolute** path; `null` for a model-level finding, to keep) matches, once made relative to the repository root (`os.path.relpath`), a line of `git diff --name-only origin/main...HEAD` (this needs a full clone, `fetch-depth: 0`).
- **Dictionary up to date**: `python "$LEAN" catalog "$PROJECT" > DATA_DICTIONARY.md`, then `git diff --exit-code -I '^> Generated on ' DATA_DICTIONARY.md` (Git 2.30+; `-I` ignores the date line): the build fails when the versioned dictionary no longer matches the model (`powerbi-documentation`).
- **Tests**: the control queries in `tests/` need an engine and data; they do not run in this CI without a connection (`powerbi-testing`).
- **Best Practice Analyzer** (Tabular Editor): optional complement for model rules; add it as a separate step depending on the version and licence of the tool the team has.
- **Several projects in one repository**: one run per project folder (job matrix).

## What the CI does not replace

Human review, business acceptance, testing the security roles and checking the values in Power BI Desktop. A green CI means "no blocking finding detectable in the files", not "ready for production".
