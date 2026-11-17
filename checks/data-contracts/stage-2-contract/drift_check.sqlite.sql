-- data-contracts, stage 2: definition drift check, SQLite version. Version 0.1.1, license MIT.
-- Status: tested on the sample data in SQLite, 17 Nov 2026 (typed table, all-text CSV import, and flags written as true/false).
-- Expected on sample/customers.csv: customers_checked 36, disagreeing 0, disagreeing_pct 0.0, unreadable_rows 0
-- Expected on sample/customers_after_change.csv: customers_checked 36, disagreeing 15, disagreeing_pct 41.67, unreadable_rows 0
-- Read-only: one select, no writes. Same logic as drift_check.postgres.sql.
-- Table: customers(customer_id, last_order_at text, is_active_customer integer, is_test integer,
--                  flag_computed_at text), times as 'YYYY-MM-DD HH:MM:SS'.
-- Flags may be stored as 1/0, true/false, t/f or yes/no, typed or as text. Any other value (blank included)
-- is not guessed: the row is counted in unreadable_rows and left out of the comparison.
-- If customers_checked is 0, the check did not run. If unreadable_rows is above 0, fix the data first.
-- Neither is a pass.
with flags as (
  select last_order_at, flag_computed_at,
         case when lower(trim(cast(is_active_customer as text))) in ('1', 'true', 't', 'yes') then 1
              when lower(trim(cast(is_active_customer as text))) in ('0', 'false', 'f', 'no') then 0 end as active_flag,
         case when lower(trim(cast(is_test as text))) in ('1', 'true', 't', 'yes') then 1
              when lower(trim(cast(is_test as text))) in ('0', 'false', 'f', 'no') then 0 end as test_flag
  from customers
),
checked as (
  select active_flag
           is not coalesce(nullif(last_order_at, '') >= datetime(flag_computed_at, '-90 days'), 0)
           as disagrees
  from flags
  where test_flag = 0 and active_flag is not null
)
select (select count(*) from checked) as customers_checked,
       (select coalesce(sum(disagrees), 0) from checked) as disagreeing,
       (select round(100.0 * sum(disagrees) / nullif(count(*), 0), 2) from checked) as disagreeing_pct,
       (select count(*) from flags where test_flag is null or (test_flag = 0 and active_flag is null)) as unreadable_rows;
