-- day-one-metric, Postgres version. Version 0.1.1, last reviewed 2026-11-17, license MIT.
-- Status: tested on a local PostgreSQL 16 with the sample data, 7 Nov 2026. Not run on a live production database.
-- Expected result on the sample: cohort_week 2026-10-26, cohort_size 48, activated 16 (33.3), active_week2 15 (31.3)
-- Read-only: one select, no writes. Run it on a replica or an export, never on the primary.
-- Tables: users(user_id, signed_up_at timestamp, source, is_internal boolean),
--         events(event_id, user_id, event_name, occurred_at timestamp).
-- If is_internal is an integer in your database, change `not is_internal` to `is_internal = 0`.
-- Change two things for your product: the as_of date below and the core action name ('recipe_cooked').
-- Same logic as cohort.sqlite.sql: weeks start on Monday, a signup week appears only once it is
-- 21 days old at the as-of date.
with params as (select timestamp '2026-11-16 00:00:00' as as_of),
cohort as (
  select u.user_id, u.signed_up_at, date_trunc('week', u.signed_up_at)::date as cohort_week
  from users u, params p
  where not u.is_internal
    and date_trunc('week', u.signed_up_at) + interval '21 days' <= p.as_of
),
core as (
  select e.user_id,
         extract(epoch from (e.occurred_at - u.signed_up_at)) / 86400.0 as days_after
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
