# Changelog

All notable changes to this repository, in plain words. Each check has its own version.

## 0.2.1, 2026-11-17

Fixes from a first public review. Both checks now work on real exports, not only the sample.

- day-one-metric 0.1.1: the SQLite query works on a plain CSV import (every column text) and accepts 0/1 or true/false; it no longer returns zero rows without saying why. The calculator converts timestamps with an offset (Postgres exports) to UTC instead of crashing, stops on a blank or unknown insider flag instead of counting it as a real user, and stops on an event name that matches nothing, listing the names it found. It also prints how many core action rows it matched.
- data-contracts 0.1.1 (moved from `contracts/` to `checks/data-contracts/`): the SQLite drift check reads flags written as 1/0, true/false, t/f or yes/no, and reports any other value in a new `unreadable_rows` column instead of guessing. The check path in `contract.yaml` is now correct.
- New `tools/run_sqlite.py`: runs any SQLite query in the repository on CSV files with Python alone, read-only, so the sqlite3 command line is not needed.
- Skills: changes go on a branch and a pull request, never merged or pushed to main by the agent; export only the columns a check needs, never personal data.
- README: a five-minute start, the exact lines for Claude Code and Cursor, version and license notes.

## 0.2.0, 2026-11-11

Contracts: one data contract per stage. A plain meanings file for before launch, a small YAML contract with a drift check (SQLite and Postgres) that recomputes a flag from raw data for first paying customers, and the same contract in the Open Data Contract Standard v3.2.0 for a team with a first data person. It includes a skill for coding agents and a synthetic sample with the expected result.

## 0.1.0, 2026-11-07

First check: day-one-metric. It counts, for the real sign-ups of each signup week or month, how many did the core action in the first period and how many in the next one, with the counts beside the percentages. It includes a SQL query for SQLite and Postgres, a calculator for two CSV exports, a spreadsheet recipe, a skill for coding agents and a synthetic sample with the expected result.
