Run `python3 -m jobs.export data/invoices.json data/customers.json revenue.json`.
Each invoice belongs to exactly one customer identified by (tenant_id, customer_id).
Unknown customers are errors (ValueError from enrich), never silently dropped.
Customer rows may share numeric ids across tenants but not within a tenant.
Sum integer cents by tenant_id, including credits. Sort tenant keys. Input data
is immutable. Customer display names do not determine tenant identity.
