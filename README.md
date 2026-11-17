# data-foundations

Data rules your coding agent follows, until you hire a data person.

Each check here is a rule file your coding agent follows (`SKILL.md`), plus the query or script that runs it and a sample with the expected result. They cover the data mistakes that cost a young company the most and show up least: a wrong number looks exactly like a right one, so each check pairs a failure with a guardrail and a test you can run yourself.

## Who it is for

Startups with no data person, their founders and engineers, and the coding agents that work for them (Claude Code, Cursor and similar). If you already have a data team, the checks still work, but they are written for people who do not.

## What is in it

| Check | What it answers | Stage |
|---|---|---|
| [day-one-metric](checks/day-one-metric/README.md) | Of the real people who signed up, how many did your core action in their first week, and how many in the second? | Before launch, first paying customers, growing with a first data person |
| [data-contracts](checks/data-contracts/README.md) | Does every key field have a written meaning, two owners and a check that tests the meaning, not only the structure? One right-sized contract per stage. | Before launch, first paying customers, growing with a first data person |

More checks follow as they are tested. Background posts: [what to measure from day one](https://goagentdata.com/posts/day-one-metric) and [data contracts for agents](https://goagentdata.com/posts/data-contracts-test-meaning).

## Start in five minutes

Nothing to install. Everything runs on Python 3 or plain SQL, with no packages.

**1. Prove it on the sample.** From the repository root:

```
python3 checks/day-one-metric/day_one_metric.py --users checks/day-one-metric/sample/users.csv --events checks/day-one-metric/sample/events.csv --event recipe_cooked --as-of 2026-11-16
python3 tools/run_sqlite.py --sql checks/data-contracts/stage-2-contract/drift_check.sqlite.sql --csv customers=checks/data-contracts/sample/customers.csv
```

Compare with each check's `sample/expected-output.txt`.

**2. Give it to your coding agent.** Copy the check folder into your repository (for example `checks/day-one-metric/`), then add one line to your agent's instructions file.

Claude Code, in `CLAUDE.md`:

```
For activation, retention or signup cohort questions, follow checks/day-one-metric/SKILL.md.
Before changing or using a field listed in contracts/, follow contracts/SKILL.md.
```

Cursor, in a rule file such as `.cursor/rules/data.mdc`:

```
---
description: Data checks for metrics and contracted fields
alwaysApply: false
---
For activation, retention or signup cohort questions, follow checks/day-one-metric/SKILL.md.
Before changing or using a field listed in contracts/, follow contracts/SKILL.md.
```

Other agents: paste the same lines wherever the agent reads its standing instructions. A `SKILL.md` is plain Markdown, so any agent can follow it.

**3. Without a coding agent.** Each check's README has a spreadsheet or plain-text path.

## Safe by default

Every check reads data and prints a result. None writes to a database or a file. The SQLite queries also run under a read-only guard in `tools/run_sqlite.py`. Any change a check suggests goes on a branch and through a pull request that a person approves; the skills tell the agent never to merge or push to the main branch. The skills guide the agent; your database access settings are what enforce it, so give the agent read-only access.

The checks stop or flag rather than guess: a blank test-account flag, an unknown event name or an unreadable value is reported, never silently counted.

## Versions

The repository version is in [CHANGELOG.md](CHANGELOG.md) and tagged on GitHub. Each check also carries its own version in its README. Example contracts inside a check have their own `version` or `contract_version` field: that is the version of the example contract, not of this kit.

## Licenses

Code, queries, contract templates and `SKILL.md` rule files are MIT, see [LICENSE](LICENSE). Guides and explanations (the README files) are CC BY 4.0, see [LICENSE-CONTENT.md](LICENSE-CONTENT.md).

## More

Posts and background are at https://goagentdata.com. Issues are open. Pull requests are reviewed before they are merged.
