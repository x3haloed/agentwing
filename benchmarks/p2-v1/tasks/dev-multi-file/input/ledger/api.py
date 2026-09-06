from .store import select
def list_items(records, limit=10):
    return [r for r in select(records, limit) if not r.get('archived', False)]
