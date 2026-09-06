SELECT DATE(activity_at) AS report_day, COUNT(*) FROM retention_events WHERE state <> 'void' GROUP BY DATE(activity_at);
