-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS instrument;
DROP TABLE IF EXISTS part;

CREATE TABLE instrument (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    description TEXT UNIQUE NOT NULL,
    hostname TEXT UNIQUE NOT NULL,
    port INTEGER DEFAULT 5025
);

CREATE TABLE part (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    global_trade_item_number TEXT UNIQUE NOT NULL,
    number TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL
);
