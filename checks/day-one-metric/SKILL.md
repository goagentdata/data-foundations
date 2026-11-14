---
name: day-one-metric
description: Use when asked for activation, retention, signup cohorts or "how many new users came back", or to build a first product metric for a startup with no data person. Computes the share of real sign-ups who did the core action in their first week and in the second, read-only.
---

# Day-one metric

Two counts over the same group of real sign-ups: did the core action within 7 days of their own signup, and in days 7 to 13. Monthly products use 30 days and days 30 to 59. Business products count accounts. Guide: README.md in this folder.

## Safe defaults
- Read-only. Use a replica or an export. Never write to production.
- Any change goes through a pull request a person approves. Never commit it yourself.
- Never change a definition without approval from its named owner.
- You guide the work. Read-only database access is what enforces it. If you were given write access, say so in the report.

## Steps
1. Find the data. Look for a users table (id, signup time, source) and an events table (user id, event name, time), or ask for two CSV exports. Check other sources a person may keep as records (billing, CRM) only to name them in the report, not to query them.
2. Find the insider flag, a column marking the team, friends and test accounts. If it is missing, do not add it. Propose it as a pull request, with how the flag will be filled (team email domain, list of ids, test devices), and run with the flag unavailable only if a person says so. State plainly that the number then includes insiders.
3. Ask a person to confirm the core action event name. Do not guess it, and do not use an app open or a finished welcome tour. Record the answer.
4. Choose the window: week for products used often, month for products used monthly. Ask a person if unsure.
5. Run on a replica or export. Options: `cohort.sqlite.sql` or `cohort.postgres.sql` (change the as-of date and the event name only), or `python3 day_one_metric.py --users users.csv --events events.csv --event <name> --as-of <YYYY-MM-DD>`. Use `--by-source` only once a source has a few dozen users.
6. First run the check on `sample/` and compare with `sample/expected-output.txt`. If it does not match, stop and report.
7. Report a table: one row per closed cohort with cohort size, counts beside percentages, and the 95 percent interval. Use the calculator for intervals.
8. Name what was left out: cohorts not yet closed (the signup count), and insiders removed (the count). Say a cohort under 30 users should be read by counts, not percentage.
9. Close the report with three lines: the event and window used, who owns the insider list, and who owns the definition. If nobody does, write "owner needed" and ask for a name.

## Never
- Write to production, or run a query that changes data.
- Add the insider flag or edit a definition directly.
- Report a percentage without its count.
- Include insiders unless a person asked for it, and then say so on the first line of the report.
- Report a cohort whose window has not closed.
- Draw a conclusion about whether the product works from one cohort.
