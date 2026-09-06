def select(records, limit):
    return sorted(records, key=lambda row: row['id'])[:limit]
