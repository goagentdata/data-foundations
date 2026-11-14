-- contracts, stage 2: definition drift check, SQLite version. Version 0.1.0, license MIT.
-- Status: tested on the sample data in SQLite, 11 Nov 2026.
-- Expected on sample/customers.csv: customers_checked 36, disagreeing 0, disagreeing_pct 0.0
-- Expected on sample/customers_after_change.csv: customers_checked 36, disagreeing 15, disagreeing_pct 41.67
-- Read-only: one select, no writes. Same logic as drift_check.postgres.sql.
-- Table: customers(customer_id, last_order_at text, is_active_customer integer, is_test integer,
--                  flag_computed_at text), times as 'YYYY-MM-DD HH:MM:SS'.
-- The casts make it work on a CSV imported as text too. If customers_checked is 0, the check did not run:
-- look at how the table was loaded before reading the result as a pass.
with checked as (
  select cast(is_active_customer as integer)
           is not coalesce(nullif(last_order_at, '') >= datetime(flag_computed_at, '-90 days'), 0)
           as disagrees
  from customers
  where coalesce(cast(is_test as integer), 0) = 0
)
select count(*) as customers_checked,
       sum(disagrees) as disagreeing,
       round(100.0 * sum(disagrees) / nullif(count(*), 0), 2) as disagreeing_pct
from checked;
