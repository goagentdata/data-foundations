-- day-one-metric, SQLite version. Version 0.1.1, last reviewed 2026-11-17, license MIT.
-- Read-only: one select, no writes. Run it on a copy of the data, a replica or an export.
-- Tables: users(user_id, signed_up_at, source, is_internal), events(event_id, user_id, event_name, occurred_at).
-- Change two things for your product: the as_of date below and the core action name ('recipe_cooked').
-- Works on typed tables and on a plain CSV import, where every column is text: is_internal may be 0/1 or
-- true/false. A blank or unknown is_internal is not counted as a real user (fix the flag, do not guess).
-- 0 rows means no cohort has closed at the as-of date, or the tables were not loaded: check both before
-- reading it as a result. Try it without the sqlite3 CLI: python3 tools/run_sqlite.py (see README).
-- Tested on the sample in ./sample (SQLite, 17 Nov 2026, typed and all-text tables). Expected result on the sample:
--   cohort_week 2026-10-26, cohort_size 48, activated 16 (33.3), active_week2 15 (31.3)
-- Week cohorts, real users only: share who did the core action in days 0 to 6 (activation)
-- and in days 7 to 13 after their own signup; a signup week appears only once every member's window has closed
with params as (select '2026-11-16 00:00:00' as as_of),
cohort as (
  select user_id, date(signed_up_at, '-6 days', 'weekday 1') as cohort_week
  from users, params
  where lower(trim(cast(is_internal as text))) in ('0', 'false', 'f', 'no')
    and datetime(date(signed_up_at, '-6 days', 'weekday 1'), '+21 days') <= as_of
),
core as (
  select e.user_id,
         julianday(e.occurred_at) - julianday(u.signed_up_at) as days_after
  from events e
  join users u on u.user_id = e.user_id
  where e.event_name = 'recipe_cooked'
),
week1 as (select distinct user_id from core where days_after >= 0 and days_after < 7),
week2 as (select distinct user_id from core where days_after >= 7 and days_after < 14)
select c.cohort_week,
       count(*) as cohort_size,
       count(w1.user_id) as activated,
       round(100.0 * count(w1.user_id) / count(*), 1) as pct_activated,
       count(w2.user_id) as active_week2,
       round(100.0 * count(w2.user_id) / count(*), 1) as pct_week2
from cohort c
left join week1 w1 on w1.user_id = c.user_id
left join week2 w2 on w2.user_id = c.user_id
group by c.cohort_week
order by c.cohort_week;
