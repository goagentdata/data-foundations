# day-one-metric

```
name: day-one-metric
stage: Before launch, First paying customers, Growing with a first data person
business_model: all
version: 0.1.1
last_reviewed: 2026-11-17
license: MIT
check: python3 day_one_metric.py --users sample/users.csv --events sample/events.csv --event recipe_cooked --as-of 2026-11-16
       prints cohort 2026-10-26 with 48 users, period 1 16 of 48 (33.3%), period 2 15 of 48 (31.3%)
```

## What is the metric, in plain words?

Two counts over the same group of real sign-ups. Take everyone who signed up in a given week, leave out your team, friends and test accounts, and count:

1. how many did the core action within 7 days of their own signup (activation), and
2. how many did it in days 7 to 13 after their own signup (the start of retention).

The core action is what your product exists to do: a recipe cooked, a ride completed, a report sent. It is not an app open or a finished welcome tour.

Two variations. A product people use monthly uses 30 days and days 30 to 59, and groups sign-ups by calendar month. A business product counts accounts, not users, so use one row per account.

Always show the count beside the percentage. "15 of 48" tells a reader more than "31%".

## What does it need?

- A users table with one row per user: an id, the signup time, a source (where the user came from) and an insider flag (1 for your team, friends and test accounts).
- An events table with one row per action: user id, event name, time.
- Or the same two things as CSV exports, with the columns `user_id, signed_up_at, source, is_internal` and `user_id, event_name, occurred_at`.

If the insider flag does not exist yet, that is the first thing to add. Ask whoever builds the product for it. A named person keeps the list.

## What fakes this number, and how do you check?

**Insiders in the count.** Your team and friends use the product more than strangers do, so they lift the number and tell you little about the market. In the sample, 12 of 60 sign-ups are insiders and the number reads 45 percent with them and 31 percent without.
Guardrail: a named owner keeps the insider list, and every number leaves insiders out by default.
Check: count the insiders in your newest closed signup week, then recompute without them. The calculator prints the number it left out, and prints a warning if you ask it to include them.

**One blended number.** A single figure across all weeks and channels lets one big cohort or one channel set the result.
Guardrail: one row per signup week, with the cohort size on the row, and the source recorded.
Check: once a source has a few dozen users, split by source (`--by-source`) and see whether the groups differ.

**"Came back" left undefined.** If nobody wrote down which event counts, a dashboard will fill the gap with app opens or logins, which say little about value.
Guardrail: one written line beside the number: which event, which window, and who owns the definition.
Check: ask a teammate to name the event behind the number. If they cannot, write the line first.

**A base too small.** With few users, moving two of them changes the story.
Guardrail: counts beside percentages, an interval around each percentage, and a note on small cohorts.
Check: the calculator prints a 95 percent interval and a "small cohort" line under 30 users. If moving two users changes your conclusion, do not act on it yet.

One more trap sits in the timing. A signup week is only reported once every member's window has closed, so a half-finished week cannot sit next to a full one. The calculator and both queries apply this rule. Only the calculator says how many signups it left out; the queries simply do not show the open week.

## Spreadsheet path (no code)

For anyone with two exports and a spreadsheet.

1. Put the users in one sheet (`user_id`, `signed_up_at`, `source`, `is_internal`) and the events in another (`user_id`, `event_name`, `occurred_at`). Make sure the times are real date-times, not text.
2. In the users sheet, add three columns. Assuming users start at row 2 and the events sheet is named Events, with columns A to C:
   - Activated, days 0 to 6: `=IF(COUNTIFS(Events!A:A,A2,Events!B:B,"recipe_cooked",Events!C:C,">="&B2,Events!C:C,"<"&B2+7)>0,1,0)`
   - Active, days 7 to 13: the same formula with `">="&B2+7` and `"<"&B2+14`.
   - Signup week: `=INT(B2)-WEEKDAY(B2,3)` (the Monday of the signup week).
3. Make a pivot table. Rows: signup week. Filter: is_internal equals 0. Values: count of users, sum of Activated, sum of Active.
4. Delete rows for weeks that started less than 21 days before today's date. Those are not closed.
5. Divide the sums by the count to get percentages, and keep the counts beside them.

Built this way on the sample rows, the pivot returns 16 of 48 and 15 of 48.

## SQL path

Two queries, same logic: `cohort.sqlite.sql` (tested on the sample in SQLite) and `cohort.postgres.sql` (tested on the sample in a local PostgreSQL 16, not run on a live production database).

Change two things: the as-of date in the `params` line and the event name `recipe_cooked`. Weeks start on Monday. For a business product, replace users with accounts. Run them on a replica or an export, never on the production primary.

On two CSV exports, with Python 3 and nothing else, from the repository root:

```
python3 tools/run_sqlite.py --sql checks/day-one-metric/cohort.sqlite.sql --csv users=checks/day-one-metric/sample/users.csv --csv events=checks/day-one-metric/sample/events.csv
```

With the sqlite3 command line (a plain `.import` loads every column as text, which the query handles), then Postgres:

```
sqlite3 sample.db
.mode csv
.import checks/day-one-metric/sample/users.csv users
.import checks/day-one-metric/sample/events.csv events
.read checks/day-one-metric/cohort.sqlite.sql

psql -f cohort.postgres.sql
```

On the sample, both return one row: cohort 2026-10-26, size 48, activated 16, active in period 2 15. Zero rows means no week has closed at the as-of date, or the tables were not loaded: check both before reading it as a result. In SQLite a blank or unknown `is_internal` is not counted as a real user. The queries do not compute intervals. The calculator does.

## Calculator path (Python, standard library only)

```
python3 day_one_metric.py --users users.csv --events events.csv --event recipe_cooked --as-of 2026-11-16
```

Options: `--period week|month` (default week), `--by-source`, and `--include-insiders` (off by default, and loud when on). It stops with a plain message, not a wrong number, when an `is_internal` value is blank or unknown, or when no event has the name you gave (it lists the names it found). Timestamps with an offset such as `+00:00` (Postgres exports) are converted to UTC. Run `python3 day_one_metric.py --help` for the input format and more examples. The script reads two files and prints text. It writes nothing. The month rule is documented in `--help`: a month cohort is reported once its start plus 60 days plus the month length has passed.

## Safe defaults

- Read-only. Run on a replica or an export, never on the production primary.
- Never a write to production. The checks only read.
- Any change the check suggests, such as adding an insider flag, goes through a pull request that a person approves.
- A named person owns the insider list and the definition. An agent never changes a definition on its own.
- This guide guides the agent. Read-only database access is what enforces it.

## What it does not do

- It does not choose your core action. A person confirms it, and the choice stays a hypothesis until cohorts are large enough to compare.
- It does not tell you whether the product works. It tells you what share of real sign-ups did the action, with a range.
- It does not find insiders. It uses the flag you give it. Unflagged friends and test accounts stay in.
- It does not fix time zones. All timestamps are treated as one timezone.
- It does not cover billing, CRM or ad spend. Add those as separate checks.
- Intervals assume sign-ups are independent. They are a guide to noise, not a guarantee.

## Sample result

The sample in `sample/` is synthetic. 60 users signed up in the week of Monday 26 October 2026, 12 flagged as insiders, 48 real. As of 16 November 2026:

| Group | Users | Period 1 (days 0 to 6) | Period 2 (days 7 to 13) |
|---|---|---|---|
| Real users | 48 | 16 (33.3%, interval 21.7 to 47.5) | 15 (31.3%, interval 19.9 to 45.3) |
| Insiders included | 60 | 28 (46.7%) | 27 (45.0%) |

With an as-of date of 15 November the week is not closed, no cohort is reported and 60 signups are left out. With `--by-source`, invite has 30 users and 10 in period 2, and store has 18 users and 5 in period 2. The exact outputs are in `sample/expected-output.txt`.
