# `AI_INSTRUCTIONS.md` template

The file lives at the project root, next to the `.pbip`, and is versioned with it. It has two parts:

- **Part A** is the text applied to the model as AI instructions. Only this part is pasted in the Prep data for AI dialog (at the time of writing the documentation states that instructions cannot be uploaded from a file in Power BI Desktop, and that a character limit applies: check it).
- **Part B** is a project register that is **not** applied: the AI data schema scope and the verified answers, so that both can be reviewed and recreated.

Writing rules:

- Every definition comes from `KPI.md` or `SCOPE.md`. Mark `TO CONFIRM` what the business has not decided; do not apply a `TO CONFIRM` line to the model.
- Reference objects by their exact model name: `[Measure]`, `Table[Column]`.
- Short imperative sentences, grouped by theme. One rule per line. No contradiction between lines, nor with a verified answer.
- No real value, customer name, person, e-mail, secret or internal-only remark. The text is stored in the model.
- Do not repeat what a description already says well: fix the description instead (`powerbi-conventions`).
- The model follows instructions as guidance, not as rules: anything that must hold (access, a mandatory filter) is enforced in the model, not asked for here.

## Template

```markdown
# AI instructions — <model name>

| | |
|---|---|
| Model | <Name>.SemanticModel |
| Business owner | <role, not a person's e-mail> |
| Last applied to the model | YYYY-MM-DD, by <role>, environment <dev / test / prod> |
| Last question-set run | YYYY-MM-DD, pass rate <n>% (see tests/AI_QUESTIONS.md) |

## Part A — Instructions applied to the model

### Purpose and audience
- This model answers questions about <business process> for <audience>.
- It covers <scope: entities, period, perimeter>. It does not cover <out of scope>.

### Glossary and synonyms
- "<business term>" or "<synonym>" means <model object>.

### Measures to use for ambiguous terms
- When the user says "<ambiguous term>" with no qualifier, use <measure>. (K-xxx)
- Use <measure A>, not <measure B>, for <case>.

### Time
- Default date: <Table[Column]>. Use <other date> only when the user asks for <case>.
- Default period when none is given: <period>.
- Fiscal year: <rule>.

### Currency and units
- Amounts are in <currency>, <net / gross of tax>.
- <Measure> is a <ratio / count / amount>; do not sum it across <dimension>.

### Do not answer
- Do not answer questions about <topic outside the model>: say the model does not cover it.
- If "<term>" could mean <A> or <B>, ask which one.

### Formatting
- <Rounding, percentage display, default breakdown>.

## Part B — Register (not applied to the model)

### AI data schema scope
| Table | Included objects | Excluded objects | Reason |
|---|---|---|---|

### Verified answers
| # | Question answered | Report / page / visual | Trigger phrases | Filters left to the user | Fixed filters | Set on (date, environment) |
|---|---|---|---|---|---|---|

### Open points
- TO CONFIRM: <question for the business owner>
```

## Example (fictitious)

On the shared example model. Names and rules are illustrative.

```markdown
## Part A — Instructions applied to the model

### Purpose and audience
- This model answers questions about product sales and margin for sales managers.
- It covers invoiced sales by customer, product, store and day. It does not cover orders not yet invoiced, stock or payroll.

### Glossary and synonyms
- "sales", "revenue" or "turnover" means [Net Sales].
- "margin" means [Gross Margin]; "margin rate" means [Gross Margin %].
- "customers" or "active customers" means [Customer Count].
- "target" or "budget" means [Sales Target].
- "store" or "shop" means Dim_Store.

### Measures to use for ambiguous terms
- For growth or "versus last year", use [Net Sales Change %]. Do not compute it from [Net Sales] and [Net Sales PY]. (K-004)
- For a margin percentage, use [Gross Margin %]. Never average a percentage across rows.
- For year to date, use [Net Sales YTD].

### Time
- Default date: Dim_Date[Date], which follows Fact_Sales[OrderDate]. Use the delivery date only when the user explicitly asks for delivered sales.
- When no period is given, answer for the current year to date and say so.
- The fiscal year is the calendar year.

### Currency and units
- Amounts are in the company's reporting currency, net of tax, after discounts and returns.
- [Customer Count] is a distinct count: do not add it up across months or stores.

### Do not answer
- Do not answer questions about individual employees or about forecasts: say the model does not cover them.
- If "performance" could mean sales, growth or margin, ask which one.

### Formatting
- Amounts without decimals; percentages with one decimal.
- When a breakdown is asked without a dimension, break down by month.

## Part B — Register (not applied to the model)

### AI data schema scope
| Table | Included objects | Excluded objects | Reason |
|---|---|---|---|
| _Measures | [Net Sales], [Net Sales PY], [Net Sales YTD], [Net Sales Change %], [Gross Margin], [Gross Margin %], [Customer Count], [Sales Target] | intermediate measures prefixed `_` | Helpers are not business metrics |
| Dim_Customer | visible attributes | CustomerKey | Key |
| Fact_Sales | NetAmount, Quantity, OrderDate (dependencies of the measures) | other columns | Users go through measures |
| Param_Metric | none | whole table | Field parameter, report use only |

### Verified answers
| # | Question answered | Report / page / visual | Trigger phrases | Filters left to the user | Fixed filters | Set on (date, environment) |
|---|---|---|---|---|---|---|
| VA-01 | Net sales by month against target | Sales / Overview / "Net sales vs target by month" | "What are net sales by month compared to target?"; "Show me monthly sales against the budget"; "How are we doing versus target this year?"; "Net sales and sales target over time"; "Monthly revenue compared with the target" | store, product category | none | YYYY-MM-DD, test |

### Open points
- TO CONFIRM: does "active customer" require a purchase in the last 12 months?
```
