#!/usr/bin/env python3
"""Day-one metric calculator. Standard library only. Read-only: it reads two CSV files and prints text.

Two counts over the same group of real sign-ups:
  period 1: did the core action in the first 7 days after their own signup (month: 30 days)
  period 2: did the core action in days 7 to 13 after their own signup (month: days 30 to 59)

License: MIT. Part of goagentdata/data-foundations, check day-one-metric, version 0.1.0.
"""
import argparse
import csv
import math
import sys
from collections import OrderedDict
from datetime import date, datetime, timedelta

EPILOG = """
input files
  users.csv   columns: user_id, signed_up_at, source, is_internal   (is_internal: 0/1 or true/false)
  events.csv  columns: user_id, event_name, occurred_at
  Timestamps look like 2026-10-26 09:00:00 or 2026-10-26T09:00:00, with an optional trailing Z.
  All timestamps are treated as the same timezone. Extra columns are ignored.

how a cohort is built
  Week: signups are grouped by the Monday of their signup week. Month: by calendar month.
  A cohort is reported only when its whole window has closed at the as-of date:
    week:  cohort start + 21 days <= as-of date  (last signup 6 days in, then 14 days of window)
    month: cohort start + 60 days + length of the month in days <= as-of date
  Cohorts that have not closed are not shown. The number of signups left out is printed.
  Insiders (is_internal true) are left out unless you pass --include-insiders.

examples
  python3 day_one_metric.py --users users.csv --events events.csv --event recipe_cooked --as-of 2026-11-16
  python3 day_one_metric.py --users users.csv --events events.csv --event recipe_cooked --as-of 2026-11-16 --by-source
  python3 day_one_metric.py --users users.csv --events events.csv --event report_sent --as-of 2026-11-16 --period month
  python3 day_one_metric.py --users users.csv --events events.csv --event recipe_cooked --as-of 2026-11-16 --include-insiders

The script never writes to a database or to any file. Run it on an export or a replica.
"""

TRUE = {"1", "true", "t", "yes", "y"}
FALSE = {"0", "false", "f", "no", "n", ""}


def parse_ts(text):
    s = text.strip()
    if s.endswith("Z") or s.endswith("z"):
        s = s[:-1]
    s = s.replace("T", " ")
    return datetime.fromisoformat(s)


def parse_flag(text, line):
    v = text.strip().lower()
    if v in TRUE:
        return True
    if v in FALSE:
        return False
    raise ValueError("is_internal must be 0/1 or true/false, got %r (users file, row %d)" % (text, line))


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, centre - half), min(1.0, centre + half))


def read_csv(path, needed):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        names = [n.strip() for n in (reader.fieldnames or [])]
        missing = [c for c in needed if c not in names]
        if missing:
            raise ValueError("%s is missing column(s): %s (found: %s)" % (path, ", ".join(missing), ", ".join(names)))
        rows = []
        for r in reader:
            rows.append({(k or "").strip(): (v or "") for k, v in r.items()})
        return rows


def month_start(d):
    return date(d.year, d.month, 1)


def month_length(d):
    nxt = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return (nxt - d).days


def cohort_key(signup, period):
    d = signup.date()
    if period == "week":
        return d - timedelta(days=d.weekday())
    return month_start(d)


def cohort_end(start, period):
    return start + timedelta(days=6 if period == "week" else month_length(start) - 1)


def closes_on(start, period):
    if period == "week":
        return start + timedelta(days=21)
    return start + timedelta(days=60 + month_length(start))


def label(start, period):
    return start.isoformat() if period == "week" else start.strftime("%Y-%m")


def line_for(name, k, n, width):
    pct = ((2000 * k + n) // (2 * n)) / 10.0 if n else 0.0  # half up, one decimal
    lo, hi = wilson(k, n)
    return "  %-*s %3d of %-3d  %5.1f%%   95%% interval %.1f to %.1f" % (width, name, k, n, pct, 100 * lo, 100 * hi)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="day_one_metric.py",
        description="Share of real sign-ups who did the core action in their first period and in the next one, by signup cohort.",
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--users", required=True, help="users CSV: user_id, signed_up_at, source, is_internal")
    ap.add_argument("--events", required=True, help="events CSV: user_id, event_name, occurred_at")
    ap.add_argument("--event", required=True, help="name of the core action event, exactly as in the events file")
    ap.add_argument("--as-of", required=True, help="date the data is complete up to, YYYY-MM-DD")
    ap.add_argument("--period", choices=["week", "month"], default="week", help="cohort and window size (default: week)")
    ap.add_argument("--by-source", action="store_true", help="also show each cohort split by source")
    ap.add_argument("--include-insiders", action="store_true", help="count insiders as users (off by default)")
    a = ap.parse_args(argv)

    try:
        as_of = date.fromisoformat(a.as_of)
    except ValueError:
        ap.error("--as-of must look like 2026-11-16")
    try:
        urows = read_csv(a.users, ["user_id", "signed_up_at", "source", "is_internal"])
        erows = read_csv(a.events, ["user_id", "event_name", "occurred_at"])
        users = OrderedDict()
        dupes = 0
        for i, r in enumerate(urows, start=2):
            uid = r["user_id"].strip()
            if uid in users:
                dupes += 1
                continue
            users[uid] = (parse_ts(r["signed_up_at"]), r["source"].strip() or "(none)", parse_flag(r["is_internal"], i))
        times = {}
        for r in erows:
            if r["event_name"].strip() != a.event:
                continue
            uid = r["user_id"].strip()
            if uid in users:
                times.setdefault(uid, []).append(parse_ts(r["occurred_at"]))
    except (OSError, ValueError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2

    w1, w2 = (7, 14) if a.period == "week" else (30, 60)
    names = ("days 0 to %d" % (w1 - 1), "days %d to %d" % (w1, w2 - 1))
    width = max(len("period 1 (%s)" % names[0]), len("period 2 (%s)" % names[1]))
    insiders = sum(1 for u in users.values() if u[2])

    print("Day-one metric: core action %s, %s cohorts, as of %s" % (a.event, a.period, as_of.isoformat()))
    if a.include_insiders:
        print("WARNING: INSIDERS ARE INCLUDED (%d of %d signups are flagged is_internal). This number is not a real-user number." % (insiders, len(users)))
    else:
        print("Insiders left out: %d of %d signups are flagged is_internal." % (insiders, len(users)))
    if dupes:
        print("Note: %d repeated user_id row(s) in the users file were ignored (first row kept)." % dupes)

    cohorts = {}
    for uid, (signed, source, internal) in users.items():
        if internal and not a.include_insiders:
            continue
        cohorts.setdefault(cohort_key(signed, a.period), []).append(uid)
    open_cohorts = set()
    total_left_out = 0
    insiders_left_out = 0
    for uid, (signed, source, internal) in users.items():
        start = cohort_key(signed, a.period)
        if closes_on(start, a.period) > as_of:
            open_cohorts.add(start)
            total_left_out += 1
            if internal and not a.include_insiders:
                insiders_left_out += 1
    shown = 0
    for start in sorted(cohorts):
        members = cohorts[start]
        if closes_on(start, a.period) > as_of:
            continue
        shown += 1

        def counts(ids):
            c1 = c2 = 0
            for uid in ids:
                signed = users[uid][0]
                days = [(t - signed).total_seconds() / 86400.0 for t in times.get(uid, [])]
                if any(0 <= d < w1 for d in days):
                    c1 += 1
                if any(w1 <= d < w2 for d in days):
                    c2 += 1
            return c1, c2

        print()
        print("Cohort %s (signups %s to %s, closed on %s)" % (label(start, a.period), start.isoformat(), cohort_end(start, a.period).isoformat(), closes_on(start, a.period).isoformat()))
        n = len(members)
        c1, c2 = counts(members)
        print("  %-*s %3d" % (width, "users", n))
        print(line_for("period 1 (%s)" % names[0], c1, n, width))
        print(line_for("period 2 (%s)" % names[1], c2, n, width))
        if n < 30:
            print("  small cohort: read the counts, not the percentage")
        if a.by_source:
            by = OrderedDict()
            for uid in members:
                by.setdefault(users[uid][1], []).append(uid)
            for src in sorted(by):
                ids = by[src]
                s1, s2 = counts(ids)
                print("  source %s: %d users, period 1 %d, period 2 %d" % (src, len(ids), s1, s2))
                print(line_for("period 1", s1, len(ids), width))
                print(line_for("period 2", s2, len(ids), width))
                if len(ids) < 30:
                    print("  small cohort: read the counts, not the percentage")

    print()
    if shown == 0:
        print("No closed cohort at this as-of date.")
    n_open = len(open_cohorts)
    print("Left out because the cohort is not closed yet: %d signups in %d cohort%s%s." % (
        total_left_out, n_open, "" if n_open == 1 else "s",
        " (%d real, %d insiders)" % (total_left_out - insiders_left_out, insiders_left_out) if total_left_out and not a.include_insiders else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
