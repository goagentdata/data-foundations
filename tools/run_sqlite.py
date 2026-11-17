#!/usr/bin/env python3
"""Run one of this repository's SQLite queries on CSV files. Standard library only. Read-only.

It loads each CSV into an in-memory SQLite database (every column as text, exactly as a plain
CSV import would), runs the query and prints the result. Nothing is written to disk.

Usage:
  python3 tools/run_sqlite.py --sql checks/day-one-metric/cohort.sqlite.sql \
      --csv users=checks/day-one-metric/sample/users.csv \
      --csv events=checks/day-one-metric/sample/events.csv

  python3 tools/run_sqlite.py --sql checks/data-contracts/stage-2-contract/drift_check.sqlite.sql \
      --csv customers=checks/data-contracts/sample/customers.csv

License: MIT. Part of goagentdata/data-foundations.
"""
import argparse
import csv
import sqlite3
import sys


def load(con, table, path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = [h.strip() for h in next(reader)]
        if not header or any(not h for h in header):
            raise ValueError("%s: the first row must name every column" % path)
        cols = ", ".join('"%s" text' % h.replace('"', '""') for h in header)
        con.execute('create table "%s" (%s)' % (table, cols))
        marks = ", ".join("?" for _ in header)
        n = 0
        for row in reader:
            if not row:
                continue
            row = (row + [""] * len(header))[: len(header)]
            con.execute('insert into "%s" values (%s)' % (table, marks), row)
            n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser(description="Run a read-only SQLite query from this repository on CSV files.")
    ap.add_argument("--sql", required=True, help="path to a .sqlite.sql file")
    ap.add_argument("--csv", action="append", required=True, metavar="TABLE=PATH", help="load PATH as table TABLE (repeat)")
    a = ap.parse_args(argv)

    con = sqlite3.connect(":memory:")
    try:
        for spec in a.csv:
            if "=" not in spec:
                ap.error("--csv must look like users=path/to/users.csv")
            table, path = spec.split("=", 1)
            n = load(con, table.strip(), path.strip())
            print("loaded %s: %d rows from %s" % (table.strip(), n, path.strip()))
        with open(a.sql, encoding="utf-8") as f:
            sql = f.read()
        # Read-only guard: the repository's queries are a single select (with optional with-clauses).
        con.execute("pragma query_only = on")
        cur = con.execute(sql)
        names = [d[0] for d in cur.description]
        rows = cur.fetchall()
    except (OSError, ValueError, sqlite3.Error) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    print()
    print(" | ".join(names))
    for r in rows:
        print(" | ".join("" if v is None else str(v) for v in r))
    if not rows:
        print("(0 rows: the query found nothing to report. Check the table names, the column names and the as-of date before reading this as a result.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
