-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS part;

CREATE TABLE part (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    global_trade_item_number TEXT UNIQUE NOT NULL,
    part_number TEXT UNIQUE NOT NULL,
    part_description TEXT UNIQUE NOT NULL
);
