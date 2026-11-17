-- data-contracts, stage 2: definition drift check, Postgres version. Version 0.1.1, license MIT.
-- Status: tested on a local PostgreSQL 16 with the sample data, 11 Nov 2026. Not run on a live production database.
-- Expected on sample/customers.csv: customers_checked 36, disagreeing 0, disagreeing_pct 0.00
-- Expected on sample/customers_after_change.csv: customers_checked 36, disagreeing 15, disagreeing_pct 41.67
-- Read-only: one select, no writes. Run it on a replica or an export, never on the primary.
-- Meaning under test (contract v1): active = placed an order in the 90 days before the flag was computed.
-- Table: customers(customer_id, last_order_at timestamp, is_active_customer boolean, is_test boolean,
--                  flag_computed_at timestamp).
-- Compare as of flag_computed_at, not now(), or every refresh boundary shows up as drift.
-- If customers_checked is 0, the check did not run. Do not read that as a pass.
-- Change three things for your field: the table, the flag column, and the rule on the "coalesce" line.
with checked as (
  select is_active_customer
           is distinct from coalesce(last_order_at >= flag_computed_at - interval '90 days', false)
           as disagrees
  from customers
  where is_test is not true
)
select count(*) as customers_checked,
       count(*) filter (where disagrees) as disagreeing,
       round(100.0 * count(*) filter (where disagrees) / nullif(count(*), 0), 2) as disagreeing_pct
from checked;
