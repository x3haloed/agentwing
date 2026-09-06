# Ledger export
Add opt-in `include_archived=False` to `ledger.api.list_items` and expose it as
`--include-archived` in `python3 -m ledger.cli`. The default must still hide archived
items. Apply the status filter before pagination; sort ascending by numeric id.
Limit must be a positive integer (ValueError in API; nonzero CLI exit). Preserve
input records. CLI accepts JSON list at --input and emits the selected JSON list.
Keep existing consumers compatible. Run `python3 -m unittest -q`.
