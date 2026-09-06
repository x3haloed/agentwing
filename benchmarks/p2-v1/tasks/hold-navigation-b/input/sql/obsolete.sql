SELECT DATE(created_at), COUNT(*) FROM warehouse.old_events WHERE status <> 'deleted' GROUP BY DATE(created_at);
