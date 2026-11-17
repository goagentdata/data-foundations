# data-contracts

```
name: data-contracts
stage: Before launch, First paying customers, Growing with a first data person
business_model: all
version: 0.1.1
last_reviewed: 2026-11-17
license: MIT
check: run stage-2-contract/drift_check.sqlite.sql on sample/customers.csv, then on sample/customers_after_change.csv
       prints 36 checked, 0 disagreeing, then 36 checked, 15 disagreeing (41.67), unreadable_rows 0 both times
```

## What is it, in plain words?

A data contract is a written, checked agreement between the people who produce or own a dataset and the people, and agents, who use it. Most contracts check structure: the column exists, has the right type, is filled and arrives on time. The costly failures change what a field means and leave its structure alone, so every one of those checks stays green.

This folder holds one right-sized contract per stage, each carrying the meaning of a field, who is counted, two named owners and a rule that a change in meaning is a breaking change. From stage 2 it also holds a check that recomputes a flag from raw data and counts the rows that disagree.

## Which one do you need?

| Stage | File | What it is | Who keeps it |
|---|---|---|---|
| Before launch | `stage-1-meanings/meanings.md` | One plain text block per key field. No tooling. | The founder owns the meanings, the developer owns the fields |
| First paying customers | `stage-2-contract/contract.yaml` and `drift_check.*.sql` | The same block as a small YAML file, plus a check that tests the meaning | A named producer owner and a named definition owner per field |
| Growing with a first data person | `stage-3-odcs/customers.odcs.yaml` | The same contract in the Open Data Contract Standard v3.2.0, so tools read it too | The data person, with versions and notice to consumers |

Start with the fields a decision depends on: paying, active, churned, revenue. A handful is enough.

## How to use it

**Without a coding agent.** Copy `stage-1-meanings/meanings.md`, replace the two example fields with yours, and keep it where the team already looks. If you use a chat assistant with exports, paste the file into its instructions.

**With a coding agent.** Copy the files for your stage, and `SKILL.md`, into a `contracts/` folder in the application repository (flat: the contract and the check side by side), and point the agent at `contracts/SKILL.md` from your agent instructions file (see the top-level README for the exact line). Copy `sample/` as well if you want the agent to prove the check on the sample first. The skill tells the agent to read the meaning before it uses a field, to stop and ask both owners before a change in meaning, and to run the check read-only. The skill guides the agent. Required reviewers on the contract file and read-only database access are what enforce it.

**The check.** Change three things in the SQL: the table, the flag column and the rule line. Run it in the producer's pipeline against a replica or a nightly export, before a change merges or nightly, so the person or agent who made the change sees it fail.

To try it on the sample, from the repository root, with Python 3 and nothing else:

```
python3 tools/run_sqlite.py --sql checks/data-contracts/stage-2-contract/drift_check.sqlite.sql --csv customers=checks/data-contracts/sample/customers.csv
python3 tools/run_sqlite.py --sql checks/data-contracts/stage-2-contract/drift_check.sqlite.sql --csv customers=checks/data-contracts/sample/customers_after_change.csv
```

Or with the sqlite3 command line (a plain `.import` loads every column as text, which the query handles):

```
sqlite3 sample.db
.mode csv
.import checks/data-contracts/sample/customers.csv customers
.read checks/data-contracts/stage-2-contract/drift_check.sqlite.sql
```

Flags may be 1/0, true/false, t/f or yes/no. Any other value, blank included, is counted in `unreadable_rows` and left out. If `customers_checked` is 0, or `unreadable_rows` is above 0, the check did not run cleanly. Do not read either as a pass.

## What it does not do

- It proves the stored flag matches the written rule. It does not prove the rule is right.
- It does not find fields that need a contract. A person picks them.
- It does not stop an owner from approving a bad change. It makes the change visible and deliberate.
- Churn and revenue rarely have one raw timestamp. Recompute them from invoices, refunds and subscription end dates, per month.

## Safe defaults

- Read-only. Run the check on a replica or an export, never on the production primary.
- Any change to a contract goes through a pull request that both owners approve.
- An agent never changes a meaning, an owner or a check's rule on its own.

## Sample result

`sample/customers.csv` and `sample/customers_after_change.csv` hold the same 40 synthetic customers (36 real, 4 test). In the second file the flag was changed from 90 days to 12 months with no change to its name or type. The check returns 0 of 36 disagreeing on the first and 15 of 36 (41.67 percent) on the second. Exact outputs: `sample/expected-output.txt`.
