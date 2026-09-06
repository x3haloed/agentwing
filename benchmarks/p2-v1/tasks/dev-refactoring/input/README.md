# Billing adapters
Both adapters round decimal text to integer cents using ROUND_HALF_UP (ties away
from zero), but duplicate the policy. Create money.to_cents(text), and have
retail.amount(text) and wholesale.amount(text) delegate to it. Preserve the
wholesale negative-value rejection and the retail ability to process refunds.
No binary floating point conversion. Decimal exponent strings are valid.
Run python3 -m unittest -q.
