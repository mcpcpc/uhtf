-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS test;

CREATE TABLE test (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    procedure_id TEXT UNIQUE NOT NULL,
    procedure_name TEXT UNIQUE NOT NULL,
    part_number TEXT UNIQUE NOT NULL
);
