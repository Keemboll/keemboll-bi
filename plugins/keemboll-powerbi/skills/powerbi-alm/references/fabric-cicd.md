# fabric-cicd — code-first promotion

Third promotion route, next to deployment pipelines and Git integration (comparison in `SKILL.md`). The repository stays the source of truth and a CI job publishes it.

## What it is

- `fabric-cicd` is a Microsoft-backed open-source Python library. It deploys Fabric items — semantic models and reports in PBIP format included — from source control to a workspace through the Fabric REST APIs.
- It orders dependencies: a semantic model is published before the reports that use it.
- Environment-specific values are swapped at deployment time with a `parameter.yml` file: `find_replace` rules, with one replacement value per environment name.
- It can remove orphan items: items present in the workspace but no longer in source control.
- The Fabric CLI command `fab deploy` uses fabric-cicd under the hood: same behaviour, driven by a configuration file instead of a Python script.
- It is a **third-party pip dependency of the BI project's CI**, not of this skill: nothing here installs or imports it.

Supported item types, Python versions, authentication options and parameter-file features **change between releases**: read the Microsoft Learn article "Deploy Power BI projects (PBIP) using fabric-cicd" and the fabric-cicd documentation before writing a deployment job, do not assert from memory.

## Before the first deployment

- Automated runs use a **service principal** with at least the Contributor role on the target workspace. The tenant must allow service principals to call the Fabric APIs: a tenant administrator decides, not the agent.
- The first deployment of a semantic model that has data sources needs the **data source credentials set by hand** in the portal (semantic model settings). Plan it in the release window; later deployments reuse them.
- Deploying a definition does not load data: plan a refresh after the deployment (`powerbi-operations`).
- Orphan removal **deletes** items from the workspace. Limit the item types in scope to what the repository really owns, and try it on a dev workspace first.

## Parameter file

Short example — replaces the dev server name held in the Power Query parameters of the model:

```yaml
find_replace:
  - find_value: "<dev-sql-server>.database.windows.net"
    replace_value:
      test: "<test-sql-server>.database.windows.net"
      prod: "<prod-sql-server>.database.windows.net"
    item_type: "SemanticModel"
    file_path: "**/expressions.tmdl"
```

- `find_value` is the value committed from dev; the keys under `replace_value` are the environment names passed to the deployment.
- Narrow each rule (`item_type`, `file_path`): an unscoped rule is applied to every file of every item in scope.
- Microsoft recommends **Variable Libraries** over `find_replace` wherever the item type supports them. Check in the Microsoft documentation whether that covers the project's items before choosing.
- fabric-cicd also documents dynamic values resolved from the target workspace (workspace and item identifiers), which avoids writing target identifiers in the file: see its parameterization guide.

## House rules

1. **Deployment credentials live in the CI secret store**, never in the repository: no client secret, certificate or token in a script, a YAML file or `parameter.yml`.
2. **No workspace or tenant identifier committed in clear if the repository is not private.** By default keep them out of the repository altogether (rule 4 of `SKILL.md`): target the workspace by name, pass identifiers through CI variables.
3. **Production deployment behind a manual approval** (protected environment or approval gate of the CI platform), after the quality gates of [release-checklist.md](release-checklist.md). A merge into `main` alone never deploys to production.
4. **The agent never runs a deployment** — locally or by triggering a pipeline — without an explicit user request for that action. It may write and review the deployment script, the workflow and `parameter.yml`.
5. Pin the version of `fabric-cicd` in the CI and upgrade it on purpose, through a PR.
6. The quality CI of [ci-examples.md](ci-examples.md) stays a separate job without secrets; only the deployment job receives the credentials.
7. No direct change in test or prod: a fix goes through the repository, then a new deployment. Rollback = redeploy the previous tag.

## What the agent reports

When asked to prepare this route: the files written, the secrets and variables the user must create in the CI platform (names only, never values), the manual steps left (service principal access, data source credentials, first refresh), and that nothing was deployed.
