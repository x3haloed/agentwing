from .store import select
def list_items(records, limit=10, include_archived=False):
    return select(records, limit, include_archived)
