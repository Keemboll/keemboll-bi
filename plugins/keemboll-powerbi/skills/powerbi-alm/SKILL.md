---
name: powerbi-alm
description: "Application lifecycle management (ALM) for a Power BI project in PBIP format: repository layout, .gitignore, branching strategy and commit format, teamwork and TMDL / PBIR merge conflicts, dev / test / prod environments, data source parameters, choosing between Fabric deployment pipelines, Git integration and fabric-cicd, quality gates before merge and before production, continuous integration (lean.py on every PR), versions and rollback. Use it to organise a BI project repository, prepare a pull request or a production release, set up CI, or decide how to promote a model or a report from one environment to the next. The mechanics (Fabric APIs) belong to the Microsoft skills. Triggers: ALM, lifecycle, Git, branch, commit, pull request, PR, merge, conflict, CI/CD, continuous integration, deployment pipeline, fabric-cicd, environment, dev test prod, production release, release, delivery, tag, version, rollback, gitignore, PBIP."
---

# powerbi-alm — lifecycle of a Power BI project

This skill sets the **house rules**: where files live, how to branch, what must be true before merging and before publishing. The **mechanics** (Fabric APIs, deployment pipelines, workspace Git integration, publishing) belong to the Microsoft skills when installed — `deployment-pipelines-authoring-cli`, `git-integration-operations-cli`, `powerbi-report-cli`, `semantic-model-authoring` — otherwise to the Fabric portal, operated by the user.

Apply `powerbi-conventions` (validation before any change, safety commit, confidentiality): those rules are not repeated here.

## Rules for the agent

1. **Read-only on production.** Never write to a production workspace, never modify a published model.
2. **No publishing, no deployment, no workspace sync** without an explicit user request for that precise action.
3. **Never an automatic `git push`, never a force-push, never a history rewrite** (`rebase` of a shared branch, `reset --hard`, `commit --amend` of a commit already pushed). The agent prepares the commits; the user pushes.
4. **Private repositories only.** No tenant, workspace or item identifier, no connection string, no token in the repository, the commit messages or the CI.
5. Before any write: clean Git tree and safety commit (`powerbi-conventions`).

## Repository layout

Default: one repository (or one top-level folder) **per BI product** — one semantic model and its reports.

```
<project>/
├── <Name>.pbip
├── <Name>.SemanticModel/     # TMDL — see powerbi-tmdl
├── <Name>.Report/            # PBIR
├── SCOPE.md  KPI.md          # requirements and indicators — powerbi-project
├── DEBT.md  CHANGES.md       # debt register and change log — powerbi-lean
├── DATA_DICTIONARY.md  REPORT.md  RELEASE_NOTES.md  # documentation — powerbi-documentation
├── SECURITY_MODEL.md         # roles, sensitivity — powerbi-governance
├── tests/                    # control queries, acceptance — powerbi-testing
├── AGENTS.md                 # instructions for agents on this project
└── .gitignore
```

- Save as **PBIP** with the model in **TMDL** and the report in **PBIR**: a `.pbix` cannot be read as a diff and cannot be versioned.
- Standard `.gitignore` and explanations: [references/gitignore-pbip.md](references/gitignore-pbip.md). Check it **before the first commit**: `cache.abf` contains the loaded data.
- Each root file has an authoritative skill; do not duplicate its content elsewhere.

## Branches and commits

Default branching model:

| Branch | Role |
|---|---|
| `main` | What is **reviewed and ready to be promoted**; the dev workspace is synced to it. Production matches the latest `vX.Y.Z` tag. Protected: no direct commit, merge through a pull request (PR). |
| `feature/<topic>` | One evolution (new page, new batch of measures). |
| `fix/<topic>` | One fix. |

- **One branch = one coherent change**, reviewable in one sitting. Do not mix a rename and a new page.
- Short-lived branches: update from `main` often, especially on the report (see conflicts).
- **PR with human review** is mandatory; the agent may prepare the description (objects touched, impact on visuals, checks done), not approve.
- Conventional commit format: `feat(model): …`, `fix(report): …`, `docs: …`, `chore: …`. A change logged in `CHANGES.md` uses the `powerbi-lean` format: `C-xxx: <summary>`, a single commit for the change and its log entry.
- A commit does not contain both an intended change and the noise of a plain Desktop save: read `git diff` and discard what is not intentional.

## Working as a team

- TMDL and PBIR split the project into **many small files** (one table per file, one visual per folder): two people touching different objects do not get in each other's way. Split the work **by table** and **by page**.
- **TMDL conflict** (measure, column): resolved by hand like code, keeping the indentation; revalidate afterwards (`powerbi-tmdl`).
- **Conflict in the JSON of a visual or a page**: **never resolve it blindly**. Pick one whole version of the file (theirs or ours), then redo the other change in Desktop.
- **`lineageTag`**: identifier unique to each object. Never copy it from one object to another, never regenerate it on an existing object; on conflict, keep the one from `main`.
- Risky files (page order, `model.tmdl`, `relationships.tmdl`, theme): one person at a time, announced to the team.
- After a merge: open the `.pbip` in Desktop and check that it loads before pushing. Syncing with Desktop: `powerbi-tmdl`.

## Environments

Default setup:

| Environment | Workspace | Who writes | Data |
|---|---|---|---|
| Dev | one per project (or per developer) | developers, the agent on request | sample or anonymised |
| Test / acceptance | one per project | promotion only | close to production |
| Prod | one per project | promotion only | real |

- Nothing environment-specific is **hardcoded** in the model: server, database and path go through **Power Query parameters**, whose value changes at promotion (deployment rules or settings of the target workspace).
- The real values of those parameters and the workspace identifiers **are not in the repository**; `SECURITY_MODEL.md` describes who has access to what (`powerbi-governance`).
- Security, labels and endorsement per environment: `powerbi-governance`.
- Refresh: scheduled in the target workspace according to the freshness set in `SCOPE.md` (`powerbi-project`); a refresh failure in production is handled before any new release.

### Three promotion routes

| | Fabric deployment pipelines | Git integration + branches | fabric-cicd (code-first) |
|---|---|---|---|
| Principle | Copies the content of one stage (workspace) to the next | Each workspace is synced with a branch; promoting = merging | A CI job publishes the item definitions of the repository to the target workspace through the Fabric REST APIs |
| Suits | small team, manual promotion from the portal, little automation | PR review at each stage, CI, several developers | a CI/CD platform already in place, a team at ease with Python and service principals |
| Source of truth | the dev workspace (Git upstream for dev only) | the repository | the repository |
| Watch out for | what is deployed can drift from the repository if someone edits in the portal | one branch per environment to maintain; per-environment settings to plan | a third-party dependency of the project's CI; deployment credentials and a parameter file to manage |

- The first two are commonly combined: **Git for dev**, pipeline for test → prod. This is the default choice.
- fabric-cicd — what it does, house rules, short example: [references/fabric-cicd.md](references/fabric-cicd.md).
- Whichever route: **no direct change in test or prod**; everything starts again from dev.
- Supported items, available deployment rules and the limits of Git integration **change over time**: check the Microsoft documentation before committing to a route, do not assert from memory.

## Quality gates

| Before merging into `main` | Before going to production |
|---|---|
| `powerbi-lean` review (`review` mode): verdict *ready to commit* | Full `powerbi-lean` audit with no blocking finding |
| Tests of the change passed (`powerbi-testing`) | Acceptance signed off (`powerbi-testing`) |
| `CHANGES.md` up to date | Security and label checked (`powerbi-governance`) |
| CI green | Documentation regenerated (`powerbi-documentation`) |
| Human review approved | Performance checked (`powerbi-performance`) |
| | Rollback plan written |

Detailed checklist: [references/release-checklist.md](references/release-checklist.md). The agent **reports** the state of each gate; it does not declare a gate passed without having checked it, and says what it could not check.

## Continuous integration

On every PR, run `lean.py audit` and `lean.py debt` (script of the `powerbi-lean` skill, read-only, standard library). The script **returns 0 even when there are findings**: a CI step reads the `--json` output and decides whether to fail. GitHub Actions and Azure DevOps examples, thresholds and how to make the script available: [references/ci-examples.md](references/ci-examples.md).

- Default threshold: fail on a **priority 1** finding or an **inconsistency** between `DEBT.md` and `CHANGES.md`; the rest is displayed, not blocking.
- The CI connects **to no workspace** and reads no data: it analyses the files of the repository.
- Optional complement: Best Practice Analyzer (Tabular Editor) for the model rules `lean.py` does not cover.

## Versions and releases

Default versioning:

- One production release = one **annotated Git tag** `vX.Y.Z` on the published commit of `main`. Major: breaking for users or connected reports (measure renamed or removed, change of grain); minor: new page, new measures; patch: everything else.
- Release note: `powerbi-documentation`. It takes the `C-xxx` entries since the previous tag.
- **Rollback**: republish the content of the previous tag (check the tag out into a `fix/rollback-vX.Y.Z` branch, then normal promotion). Never rewrite `main`. Rolling back the model does not restore the data: plan a refresh.
- The rollback plan is written **before** the production release, in the PR.

## Process — preparing a release

1. `git status` clean; branch up to date with `main`.
2. Go through the quality gates; run `lean.py audit` and `lean.py debt`.
3. Return a table gate / state / evidence / left to do, and the PR description.
4. **Stop**: merge, tag, push and promotion are done by the user, or by the agent on explicit request, one action at a time.

## References

- [references/gitignore-pbip.md](references/gitignore-pbip.md) — standard `.gitignore` and what must never be versioned.
- [references/release-checklist.md](references/release-checklist.md) — detailed quality gates and rollback plan.
- [references/ci-examples.md](references/ci-examples.md) — GitHub Actions and Azure DevOps workflows, `lean.py` exit codes.
- [references/fabric-cicd.md](references/fabric-cicd.md) — code-first promotion with the fabric-cicd library.
