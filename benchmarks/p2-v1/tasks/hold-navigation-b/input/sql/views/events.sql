CREATE VIEW retention_events AS SELECT occurred_at AS activity_at, status AS state FROM warehouse.event_log;
