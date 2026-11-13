# `tests/AI_QUESTIONS.md` template

The question set measures whether an AI consumer answers business questions with the right objects. It is run before and after each change to the model metadata or to the AI settings. Results and the approval decision are recorded in `tests/ACCEPTANCE.md` (`powerbi-testing`).

## Building the set

- **15 to 30 questions.** Fewer does not show a trend; more is rarely re-run.
- Source: the business questions of `SCOPE.md`, then what users actually type. Keep their wording, including the vague one.
- Default mix:

| Kind | Share | Example of intent |
|---|---|---|
| Direct KPI question | about half | one approved KPI, one period |
| Ambiguous term | 3 to 5 | "sales", "performance", "last year" with no qualifier |
| Time logic | 3 to 5 | year to date, versus prior year, a named month |
| Breakdown or ranking | 3 to 5 | by store, top products |
| Must not answer | 2 to 3 | outside the model scope: expected result is a refusal |
| Must ask back | 1 to 2 | expected result is a clarifying question |
| Per RLS profile | 1 per profile | same question asked as each test profile of `SECURITY_MODEL.md` |

- The expected result is the **measure, filters and shape**, taken from `KPI.md`. Never a real value, a customer name or a person.
- The business owner confirms the set. A question is changed only by them, never to make a run pass.

## Scoring

| Score | Meaning |
|---|---|
| `pass` | Right measure, right filters, expected shape. Or the expected refusal or clarifying question |
| `wrong` | An answer was given with the wrong measure, date, filter or grain. The dangerous case: it looks right |
| `refused` | No answer, an error, or a clarifying question where an answer was expected |

- Judge from the generated DAX or the consumer's explanation of how it answered, when shown; otherwise from the fields and filters visible in the answer.
- Default: one run per question, in a fresh session; a question whose result differs between two runs is scored `wrong`.
- Pass rate = `pass` / number of questions. Default target: 90%, with no `wrong` on a question tied to an approved KPI.
- For a per-profile question, `pass` also requires that the answer stays inside the profile's perimeter. A leak is a security defect: stop and apply `powerbi-testing` and `powerbi-governance`.
- Do not copy the answers into the file: only the score and a short note on which object was used.

## Template

```markdown
# AI question set — <model name>

| | |
|---|---|
| Confirmed by | <business owner role>, YYYY-MM-DD |
| Target | 90% pass, no `wrong` on an approved KPI question |

## Questions

| # | Question (as users ask it) | Kind | KPI | Expected measure | Expected filters / date | Expected shape |
|---|---|---|---|---|---|---|
| Q-01 | | | K-xxx | | | |

## Runs

| Run | Date | Consumer | Environment | After change | Run by | Pass | Wrong | Refused | Pass rate |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | YYYY-MM-DD | | | baseline | | | | | |

## Results by question

| # | R-01 | R-02 | Note (object used when not the expected one) |
|---|---|---|---|
| Q-01 | | | |
```

## Example (fictitious)

```markdown
## Questions

| # | Question (as users ask it) | Kind | KPI | Expected measure | Expected filters / date | Expected shape |
|---|---|---|---|---|---|---|
| Q-01 | What were our sales last month? | Ambiguous term | K-001 | [Net Sales] | previous calendar month on Dim_Date[Date] | one amount |
| Q-02 | How are sales doing versus last year? | Time logic | K-004 | [Net Sales Change %] | current year to date | one percentage, period stated |
| Q-03 | Margin rate by store this year | Breakdown | K-006 | [Gross Margin %] | current year, by Dim_Store | table, one row per store |
| Q-04 | How many customers did we have in the first quarter? | Direct KPI | K-007 | [Customer Count] | first quarter of the current year | one count, not a sum of months |
| Q-05 | Which stores are below target? | Ranking | K-008 | [Net Sales], [Sales Target] | current year to date | list of stores |
| Q-06 | What is the salary cost per store? | Must not answer | — | none | — | refusal: outside the model scope |
| Q-07 | How is performance? | Must ask back | — | none | — | clarifying question: sales, growth or margin |
| Q-08 | Net sales by region (asked as the one-region profile of RLS_Region) | Per RLS profile | K-001 | [Net Sales] | profile's region only | one region visible |

## Runs

| Run | Date | Consumer | Environment | After change | Run by | Pass | Wrong | Refused | Pass rate |
|---|---|---|---|---|---|---|---|---|---|
| R-01 | YYYY-MM-DD | report chat pane | test | baseline | user | 4 | 3 | 1 | 50% |
| R-02 | YYYY-MM-DD | report chat pane | test | tier 1 + AI data schema | user | 6 | 1 | 1 | 75% |

## Results by question

| # | R-01 | R-02 | Note (object used when not the expected one) |
|---|---|---|---|
| Q-01 | wrong | pass | R-01 summed Fact_Sales[NetAmount] over the delivery date |
| Q-04 | wrong | wrong | adds monthly counts; candidate for an instruction or a verified answer |
| Q-07 | refused | refused | error instead of a clarifying question |
```
