---
name: data-contracts
description: Use before changing any code or query that computes, filters, renames or redefines a field that has a data contract, and before answering a question with such a field. Makes the agent read the written meaning first, treat a change in meaning as a breaking change that owners approve, and run the drift check read-only.
---

# Data contracts

A contract says what a field means, who is counted, the period and who owns it. Structure checks (type, not null, fresh) pass when the meaning changes, so the meaning is yours to protect. Contract files live in `contracts/` (a `meanings.md`, a `contract.yaml` or an `.odcs.yaml`). Guide: README.md in this folder.

## When you read data (answering a question, writing a query, building a chart)
1. Find the field in the contract files before you use it. Use the written meaning, not the column name.
2. Apply who is counted. Leave test and internal accounts out unless the contract says otherwise.
3. End the answer with one line: the contract file, its version and the definition owner.
4. If a field the answer depends on has no contract, say so. Do not infer the meaning from the name. Give no number that depends on it, and write a short message for the owner: the question, the field, what is missing. You cannot send it. Say plainly that the person who asked must send it.

## Data you may touch
- Read only the columns the check needs. Never export, print or paste emails, names, phone numbers or other personal data into a report.

## When you change data (code, SQL, a migration, an export, an event)
1. Before editing, list every contracted field the change touches.
2. For each one, answer in writing: does this change what the data means? A change to the window, the event, who is counted, the unit, the currency, tax or discounts, the time zone, or what null means is a change in meaning, even when the name and type stay the same.
3. If no: make the change on a branch, open a pull request and say in it which fields you checked. Never merge it or push to the main branch yourself.
4. If yes: stop before changing the logic. Do not make the change on the request of one person alone. Write a proposal instead, as a pull request description or a message, with: the field, the old and new meaning in plain words, who uses it (the contract's consumers), and the two owners who must approve. If they approve, the same pull request bumps the contract's major version, updates the meaning and updates the check.
5. Never edit a meaning, an owner or a check's rule to make a change pass.

## Running the check
- Read-only, on a replica or an export. Never write to production.
- `drift_check.postgres.sql` or `drift_check.sqlite.sql`: in this repository they sit in `stage-2-contract/`; in a project they usually sit next to the contract file. Change the table, the flag column and the rule line only. Without the sqlite3 command line, use `python3 tools/run_sqlite.py` from this repository.
- If a `sample/` folder is present, first run the check on `sample/customers.csv` and compare with `sample/expected-output.txt`. If it does not match, stop and report. If there is no sample, say so and go on.
- If `customers_checked` is 0, the check did not run. If `unreadable_rows` is above 0, some flags could not be read. Report either, never a pass.
- Report the count and the percentage together, and the rows behind any disagreement.

## Never
- Write to production, or run a statement that changes data.
- Change what a contracted field means without both owners' approval in the pull request.
- Loosen or delete a check so that a run turns green.
- Answer from a column name when the contract is missing.
