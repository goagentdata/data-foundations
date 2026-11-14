# What our key fields mean

Stage 1, before launch. One short block per field a decision depends on. Start with the money fields and the flags that will go into a board or investor update. Names and people here are made up: replace them.

Rule for everyone, people and agents: if a field below is used in a number, use this meaning. If a field a decision depends on is not below, do not guess from its name. Ask the definition owner and add it here first.

## is_active_customer
- Meaning: the customer placed an order in the last 90 days.
- Who is counted: real customers. Test and internal accounts (is_test = true) are never counted.
- Period: rolling 90 days up to the time the flag was computed, UTC.
- Producer owner: Avi Cohen. Owns the field in the application and every change to it.
- Definition owner: Maya Levi. Decides what "active" means.
- Change rule: changing the window, the event or who is counted is a change in meaning. It needs the definition owner's yes before the code changes.
- Last reviewed: 2026-11-11.

## amount
- Meaning: what the customer was charged for the order, tax included, after discounts.
- Unit: the order's own currency, in minor units (cents). The currency is in `currency`.
- Who is counted: every order, including refunded ones. Refunds are separate rows in `refunds`.
- Producer owner: Avi Cohen. Definition owner: Maya Levi.
- Change rule: moving tax, discounts or refunds in or out of this field is a change in meaning.
- Last reviewed: 2026-11-11.
