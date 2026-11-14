# data-foundations

Data rules your coding agent follows, until you hire a data person.

This repository holds short, tested checks for the data mistakes that cost a young company the most and show up least. A wrong number looks exactly like a right one, so each check pairs a failure with a guardrail and a test you can run yourself.

## Who it is for

Startups with no data person, their founders and engineers, and the coding agents that work for them. If you already have a data team, the checks still work, but they are written for people who do not.

## What is in it now

One check and one set of contracts:

| Check | What it answers | Stage |
|---|---|---|
| [day-one-metric](checks/day-one-metric/README.md) | Of the real people who signed up, how many did your core action in their first week, and how many in the second? | Before launch, first paying customers, growing with a first data person |
| [contracts](contracts/README.md) | Does every key field have a written meaning, two owners and a check that tests the meaning, not only the structure? One right-sized contract per stage. | Before launch, first paying customers, growing with a first data person |

Rule packs are not published yet, and there is nothing to install.

## How to use a check

Each check folder has a guide, the code and a sample with the expected result.

**Without a coding agent.** Open the guide in the check folder and follow the spreadsheet path, or run the calculator on two CSV exports. The calculator needs Python 3 and nothing else:

```
python3 checks/day-one-metric/day_one_metric.py --users users.csv --events events.csv --event your_core_action --as-of 2026-11-16
```

Run it on the sample first and compare the output with `checks/day-one-metric/sample/expected-output.txt`.

**With a coding agent.** Point your coding agent at the check's `SKILL.md` and ask it to follow that file. The skill tells the agent to work on a replica or an export, to ask a person to confirm the core action, to propose any change as a pull request, and never to write to production. The skill guides the agent. Your database access settings are what enforce it, so give the agent read-only access.

## Safe by default

Every check reads data and prints a result. None writes to a production system. Any change a check suggests goes through a pull request that a person approves.

## Licenses

Code and rules are MIT, see [LICENSE](LICENSE). Written content is CC BY 4.0, see [LICENSE-CONTENT.md](LICENSE-CONTENT.md).

## More

Posts and background are at https://goagentdata.com. Issues are open. Pull requests are reviewed before they are merged.
