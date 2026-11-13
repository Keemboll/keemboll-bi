# RLS and OLS — examples and pitfalls

Example model: `Fact_Sales` → `Dim_Store[Region]`, security table `Dim_User[Email]`, `Dim_User[Region]` (hidden). Table names and prefixes: see `powerbi-conventions`. Addresses are fictitious (`@example.com`).

> These examples were not executed here (no engine available): test them as described in `powerbi-testing` before use.

## Static RLS

One role per scope. Simple, but roles multiply as soon as scopes change.

```tmdl
role RLS_RegionNorth
	modelPermission: read

	tablePermission Dim_Store = Dim_Store[Region] = "North"
```

## Dynamic RLS — one scope per user

```tmdl
role RLS_Region
	modelPermission: read

	tablePermission Dim_Store = Dim_Store[Region] = LOOKUPVALUE ( Dim_User[Region], Dim_User[Email], USERPRINCIPALNAME () )

	tablePermission Dim_User = Dim_User[Email] = USERPRINCIPALNAME ()
```

- `LOOKUPVALUE` returns an error if the user has **several** rows: only use this form when the security table has one row per user.
- User missing from the table: `LOOKUPVALUE` returns BLANK, no region matches, they see nothing — this is the intended behavior.

## Dynamic RLS — several scopes per user

Expression of the filter set on `Dim_Store`:

```dax
Dim_Store[Region]
    IN CALCULATETABLE (
        VALUES ( Dim_User[Region] ),
        Dim_User[Email] = USERPRINCIPALNAME ()
    )
```

`Dim_User` stays **disconnected** from the rest of the model (no relationship): the filter goes through the expression, not through a relationship.

## Hierarchy (a manager sees their team)

With a `Dim_Employee` dimension carrying `EmployeeKey`, `ManagerKey` and `Email`, and a calculated path column:

```dax
Path = PATH ( Dim_Employee[EmployeeKey], Dim_Employee[ManagerKey] )
```

Role filter on `Dim_Employee`:

```dax
PATHCONTAINS (
    Dim_Employee[Path],
    LOOKUPVALUE ( Dim_Employee[EmployeeKey], Dim_Employee[Email], USERPRINCIPALNAME () )
)
```

## `USERPRINCIPALNAME()` or `USERNAME()`

Prefer `USERPRINCIPALNAME()`: it returns the UPN (`first.last@example.com`) in the service as well as in Desktop, whereas `USERNAME()` returns `DOMAIN\user` in Desktop. DAX string comparison is case-insensitive, but the UPN may differ from the e-mail address: load the security table with the **UPN**.

## OLS

Excerpt: these `tablePermission` entries are **added** to those of the `RLS_Region` role above (RLS and OLS in the same role); they do not replace it.

```tmdl
role RLS_Region
	modelPermission: read

	tablePermission Fact_Sales
		columnPermission UnitCost = none

	tablePermission Dim_Salary
		metadataPermission: none
```

- `columnPermission ... = none` hides a column (short form; the long form places `metadataPermission: none` under `columnPermission <column>`); `metadataPermission: none` under `tablePermission` hides the whole table. Not executed here: check by exporting an existing role (TMDL view in Desktop); the TMDL syntax is authoritative in `powerbi-tmdl` and the Microsoft documentation.
- For this role, any measure that references the hidden object fails, as do the visuals that use it: plan separate measures and pages, or a conditional page.
- A relationship that relies on a hidden column keeps working as long as its table is not hidden. However, hiding a **table** located in the middle of a relationship chain (A → B → C, B hidden) is rejected at design time.

## Common pitfalls

| Pitfall | Consequence | Remedy |
|---|---|---|
| Filter set on the fact table | Slow (evaluated on the largest table); dimensions stay fully visible (customer and store names in slicers) | Filter the dimension |
| Bidirectional relationship without the security option | The role filter does not travel back | Filter the right dimension, or check the option knowingly |
| User in two roles | They see the union of both scopes | A single dynamic role |
| Test run by an Admin / Member / Contributor in the service | RLS does not apply to them: falsely reassuring test | Test "as" the role, or with a Viewer account |
| Measure with `ALL ( Dim_Store )` | Does **not** bypass RLS (the security filter stays), but "all stores" totals become "all **my** stores" | Say so in the measure description |
| Security table visible and unfiltered | Everyone reads everybody's rights | Hide it **and** filter it with the role |
| Hard-coded e-mails in the expression | Personal data in Git, impossible to maintain | Security table + groups |
| Role created but without members in the service | Viewers not attached to a role see nothing as soon as a role exists | Attach groups; record it in `SECURITY_MODEL.md` |
| Composite model / DirectQuery to another model | Rules of the source and of the model stack in non-obvious ways | Check the Microsoft documentation and test |
