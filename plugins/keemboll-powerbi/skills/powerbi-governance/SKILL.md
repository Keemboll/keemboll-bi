---
name: powerbi-governance
description: "Security and governance of a Power BI semantic model or report: row-level security (static and dynamic RLS), object-level security (OLS), sensitivity labels, endorsement (Promoted / Certified), model ownership, workspace roles, distribution through apps, Build permission, personal or health data, and the project's SECURITY_MODEL.md sheet. Use it to design, review or change security roles, decide who sees what, prepare a publication or audit the access of a project. Triggers: security, governance, RLS, row-level security, OLS, object-level security, role, USERPRINCIPALNAME, sensitivity label, certified, promoted, endorsement, workspace, workspace roles, sharing, app, audience, Build permission, access, personal data, GDPR, least privilege, security table, who sees what."
---

# Power BI governance and security

Goal: know **who sees what**, write it down, test it, and publish only what is authorized.

This skill is authoritative for the **design** of security. Authoritative elsewhere:

- `powerbi-conventions`: role naming (`RLS_<scope>`), confidentiality of the metadata read by an agent, validation process before any change.
- `powerbi-testing`: role test protocol (level 5) and acceptance record.
- `powerbi-tmdl`: syntax and editing of role files.
- `powerbi-alm`: environments and deployment; `powerbi-project`: phases and deliverables.
- `powerbi-ai-readiness`: exposing a model to Copilot or data agents (RLS / OLS still apply).
- The **mechanics** (assigning members to a role, applying a label, setting workspace access) belong to the Microsoft skills when installed (`semantic-model-authoring`, `onelake-catalog-cli`), otherwise to the Power BI / Fabric portal.

## Rules

1. **Any role creation, change or deletion** = written plan → **explicit validation** by the user → execution → test (`powerbi-testing`) → update of `SECURITY_MODEL.md`. Never "in passing" while doing another task.
2. RLS **only protects viewers**: in the service, the workspace roles Admin, Member and Contributor see all the data of the model. Security therefore starts with workspace roles.
3. Filter **dimensions**, never facts (rule from `powerbi-conventions`); here: let relationships propagate the filter.
4. **Never a hard-coded e-mail, person name or identifier** in a role expression or in `SECURITY_MODEL.md`: people are attached to **security groups** in the service, not in versioned files.
5. A user who is a member of **several roles** sees the **union** of their scopes: a role cannot restrict another one. Exception: RLS and OLS carried by different roles do not combine (error) — see OLS.
6. No publication without an identified owner; sensitivity label: rule from `powerbi-conventions`.
7. The agent **does not assign** members, share or change a label without an explicit request: these actions are visible to other people.

## RLS — row-level security

| Need | Approach |
|---|---|
| A few fixed, stable scopes (default: 2 to 5 regions) | **Static**: one role per scope, hard-coded filter on the dimension |
| Many or changing scopes, one user = one or several scopes | **Dynamic**: a single role, security table + `USERPRINCIPALNAME()` |
| Hierarchy (a manager sees their team) | Dynamic + `PATH` functions on the hierarchical dimension |

- **Dynamic**: a security table (user × scope), **hidden**, loaded from a controlled source (directory, HR reference data) — not typed by hand into the model. It is itself filtered by the role, so that a user cannot read other users' rights.
- **Propagation**: the filter follows relationships in the one → many direction. A bidirectional relationship only propagates security the other way when the *Apply security filter in both directions* option is checked; prefer filtering the right dimension directly.
- **Many-to-many**: go through a bridge table (`powerbi-data-modeling`) and check by test that the filter does reach the facts.
- **Everyone / no one**: explicitly plan for the user missing from the security table (they must see nothing) and, if needed, a separate "see everything" role rather than an exception in the formula.
- **DirectQuery / Direct Lake**: the model's RLS applies, but rules defined on the source side (warehouse, SQL endpoint) have their own effects — in particular a possible fallback to DirectQuery for Direct Lake on SQL endpoint. Check the behavior in the current Microsoft documentation before committing to a design.
- **Performance**: a role expression is evaluated on every query; keep it simple (no iterator over a large table), see `powerbi-performance`.

TMDL and DAX examples, detailed pitfalls: [references/rls-ols.md](references/rls-ols.md).

## OLS — object-level security

Hides **a whole table or column** (salary, cost, personally identifying data) from a role: for that role, the object does not exist.

- Keep it for truly sensitive columns: a visual or measure that depends on a hidden object **fails with an error** for that role. Inventory the usages first (`powerbi-lean`, `usage` subcommand).
- Defined in the TMDL view of Power BI Desktop (`createOrReplace` script of the role) or with an external tool (Tabular Editor); the "Manage roles" window does not offer it — check on the current version.
- Combine RLS and OLS in **the same role**: a user who is a member of one role carrying RLS and another carrying OLS gets an **error when queries run** (restriction documented by Microsoft).
- Hiding a column (`isHidden`) **is not** security: it can still be queried.
- Often simpler: do not load the sensitive column, or put it in a separate model with restricted access.

## Access, sharing and endorsement

| Topic | Default rule |
|---|---|
| Workspace roles | **Least privilege**: Admin = 2 owners at most; Member / Contributor = BI team only; consumers are **not** added to the workspace |
| Distribution | Through an **app** (audiences), not through direct report sharing or Viewer access to the workspace |
| Groups | Access is granted to **security groups**, never to people one by one |
| **Build** permission | Granted only to those who must create their own reports or analyze the model in Excel; it gives access to the whole model (within the limits of RLS / OLS) |
| Ownership | Each model has a **business owner** and a **technical owner** named in `SECURITY_MODEL.md` by their function; no model tied to a personal account that may disappear |
| Endorsement | **Promoted**: considered reliable by its owner. **Certified**: validated through the organization's process, by the people authorized by the administrator. Certify only after a signed acceptance (`powerbi-testing`) |
| Sensitivity label | Applied to the model and the report before publication; it follows the content (downstream inheritance, exports) depending on the tenant configuration |
| Data export | Decide per report whether exporting the underlying data is allowed; disable it for sensitive data |

## Personal and health data

- **Minimize**: load only the columns needed to answer the report's questions. No name, phone number, address or national identifier "just in case".
- Prefer **aggregates** or pseudonymized identifiers; watch out for small counts that allow re-identification (agree on a minimum display threshold).
- Report to the user any personally identifying data found in the model, **without copying it** into the answer, `DEBT.md` or `SECURITY_MODEL.md`.
- Confidentiality of what the agent itself reads: see `powerbi-conventions` (metadata confidentiality).

## Deliverable: `SECURITY_MODEL.md`

At the project root, next to the `.pbip`, versioned: role × scope matrix, attached groups (by group name), owners (by function), label, endorsement, date and result of the last test. **No person name, no e-mail, no data value.** Template: [references/security-template.md](references/security-template.md).

## Process

1. **Inventory**: existing roles (the model's `definition/roles/` folder), security tables, bidirectional relationships, sensitive columns, `SECURITY_MODEL.md` if it exists.
2. **Gather the need**: who (profiles, not people) must see what; who validates; which data is sensitive.
3. **Propose a plan**: roles created / changed / deleted, DAX expressions, impact on visuals (OLS), planned tests.
4. **Wait for explicit validation.**
5. **Execute** (`powerbi-tmdl` for the files), on a development branch (`powerbi-alm`).
6. **Test** each role as described in `powerbi-testing`; if no engine is available, provide the queries and say so.
7. **Update `SECURITY_MODEL.md`** and summarize: role / action / scope / test.

## Before publication — quick check

- [ ] Every role is tested, including the user with no rights.
- [ ] No hard-coded e-mail or name in roles, parameters or M expressions.
- [ ] Consumers go through the app, not through the workspace.
- [ ] Sensitivity label and owners are filled in.
- [ ] `SECURITY_MODEL.md` is up to date.
