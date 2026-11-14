# Changelog

All notable changes to this repository, in plain words. Each check has its own version.

## 0.2.0, 2026-11-11

Contracts: one data contract per stage. A plain meanings file for before launch, a small YAML contract with a drift check (SQLite and Postgres) that recomputes a flag from raw data for first paying customers, and the same contract in the Open Data Contract Standard v3.2.0 for a team with a first data person. It includes a skill for coding agents and a synthetic sample with the expected result.

## 0.1.0, 2026-11-07

First check: day-one-metric. It counts, for the real sign-ups of each signup week or month, how many did the core action in the first period and how many in the next one, with the counts beside the percentages. It includes a SQL query for SQLite and Postgres, a calculator for two CSV exports, a spreadsheet recipe, a skill for coding agents and a synthetic sample with the expected result.
