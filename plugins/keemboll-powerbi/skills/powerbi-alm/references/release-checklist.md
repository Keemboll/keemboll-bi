# Checklist — merge and production release

Every line is **checked**, not assumed. For each box, note the evidence (script output, screenshot, reviewer name). A box that cannot be checked is reported as such, never ticked by default.

## Before merging into `main`

- [ ] The branch contains only **one coherent change**; `git diff main...` read in full.
- [ ] No forbidden file in the diff: `cache.abf`, `localSettings.json`, `.pbix`, data extract, secret, workspace identifier.
- [ ] `powerbi-lean` review in `review` mode: verdict *ready to commit*.
- [ ] Tests of the change passed; before / after values compared for every modified measure (`powerbi-testing`).
- [ ] Rename or removal: `lean.py usage` inventory done, visuals updated, reports connected to the published model checked.
- [ ] `CHANGES.md`: `C-xxx` entry; `DEBT.md` up to date; `lean.py debt` without inconsistency.
- [ ] The `.pbip` opens in Power BI Desktop without error after the last update from `main`.
- [ ] CI green.
- [ ] Human review approved.

## Before going to production

### Quality
- [ ] `lean.py audit` on the whole project: no priority 1 finding; the remaining findings are fixed or recorded in `DEBT.md`.
- [ ] Acceptance done in the test environment and **signed off by the business** (`powerbi-testing`).
- [ ] Performance: main pages measured, no regression against the version in production (`powerbi-performance`).

### Security and governance (`powerbi-governance`)
- [ ] RLS / OLS roles tested with at least one user per role.
- [ ] Sensitivity label applied (expected by default).
- [ ] Access to the production workspace and app audience reviewed; `SECURITY_MODEL.md` up to date.

### Documentation (`powerbi-documentation`)
- [ ] `DATA_DICTIONARY.md` regenerated from the delivered model.
- [ ] Release note written from the `C-xxx` entries since the previous tag.
- [ ] `KPI.md` consistent with the delivered measures (`powerbi-project`).

### Environment
- [ ] Source parameters pointing to production (deployment rules or settings of the target workspace); no dev or test source left.
- [ ] Refresh scheduled, source credentials and gateway in place in the target workspace.
- [ ] Release window agreed; users warned if the change is breaking.

### Rollback
- [ ] Tag of the version currently in production identified.
- [ ] Procedure written in the PR: who decides, how to republish the previous tag, how long it takes.
- [ ] Change that is **not reversible** by a plain republish (change of grain, column removed at the source, incremental refresh history): flagged explicitly and accepted.

## After the production release

- [ ] Annotated tag `vX.Y.Z` set on the published commit (default versioning scheme).
- [ ] First refresh succeeded; main pages opened with a user account, not an administrator account.
- [ ] Key figures reconciled with the source or the previous version (`powerbi-testing`).
- [ ] Release note distributed; merged branch deleted.

## Who does what

| Action | Agent | Human |
|---|---|---|
| Run the scripts, read the diff, prepare the PR description and the release note | yes | — |
| Tick a box from evidence produced | yes, citing the evidence | — |
| Approve the PR, sign off acceptance | no | yes |
| Merge, tag, push, promote | on explicit request, one action at a time | yes |
| Write to production | **never directly** | through the promotion route |
