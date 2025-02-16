-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS command;
DROP TABLE IF EXISTS instrument;
DROP TABLE IF EXISTS measurement;
DROP TABLE IF EXISTS part;
DROP TABLE IF EXISTS phase;
DROP TABLE IF EXISTS protocol;

CREATE TABLE command (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL,
    scpi TEXT UNIQUE NOT NULL,
    delay INTEGER DEFAULT 0
);

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
    name TEXT UNIQUE NOT NULL,
    units TEXT DEFAULT NULL,
    lower_limit REAL DEFAULT NULL,
    upper_limit REAL DEFAULT NULL
);

CREATE TABLE part (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    global_trade_item_number TEXT UNIQUE NOT NULL,
    number TEXT UNIQUE NOT NULL,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE phase (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL,
    retry INTEGER DEFAULT 0
);

CREATE TABLE protocol (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    command_id INTEGER NOT NULL,
    instrument_id INTEGER NOT NULL,
    measurement_id INTEGER DEFAULT NULL,
    part_id INTEGER NOT NULL,
    phase_id INTEGER NOT NULL,
    FOREIGN KEY(command_id) REFERENCES command(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(instrument_id) REFERENCES instrument(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(measurement_id) REFERENCES measurement(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(part_id) REFERENCES part(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(phase_id) REFERENCES phase(id) ON DELETE CASCADE ON UPDATE NO ACTION
);
