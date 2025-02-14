-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS instrument;
DROP TABLE IF EXISTS measurement;
DROP TABLE IF EXISTS part;

CREATE TABLE instrument (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL,
    hostname TEXT UNIQUE NOT NULL,
    port INTEGER DEFAULT 5025
);

CREATE TABLE measurement (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    part_id INTEGER NOT NULL,
    instrument_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phase TEXT NOT NULL,
    scpi TEXT NOT NULL,
    units TEXT DEFAULT NULL,
    lower_limit REAL DEFAULT NULL,
    upper_limit REAL DEFAULT NULL,
    delay INTEGER DEFAULT 0,
    FOREIGN KEY(part_id) REFERENCES part(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(instrument_id) REFERENCES instrument(id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE part (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    global_trade_item_number TEXT UNIQUE NOT NULL,
    number TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL
);
