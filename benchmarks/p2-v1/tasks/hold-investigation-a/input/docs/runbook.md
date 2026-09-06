Run python3 -m billing.replay events.json balances.json.
Project events in input order. Event identity is (tenant,event_id); a duplicate
identity must be ignored even if its repeated payload differs. Different tenants
can reuse event_id. Apply signed integer delta to (tenant,account). Output keys
are tenant/account and values are balances. Include zero balances; sort keys.
Do not modify inputs. The projection must not mutate event dicts.
