def select(records, limit, include_archived=False):
    if type(limit) is not int or limit <= 0:
        raise ValueError("limit must be a positive integer")
    visible = (r for r in records if include_archived or not r.get('archived', False))
    return sorted(visible, key=lambda row: row['id'])[:limit]
