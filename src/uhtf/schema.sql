-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS command;
DROP TABLE IF EXISTS instrument;
DROP TABLE IF EXISTS measurement;
DROP TABLE IF EXISTS part;
DROP TABLE IF EXISTS phase;
DROP TABLE IF EXISTS procedure;
DROP TABLE IF EXISTS recipe;
DROP TABLE IF EXISTS setting;

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
    precision INTEGER NOT NULL,
    units TEXT DEFAULT NULL,
    lower_limit REAL DEFAULT NULL,
    upper_limit REAL DEFAULT NULL
);

CREATE TABLE part (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL,
    global_trade_item_number TEXT UNIQUE NOT NULL,
    number TEXT UNIQUE NOT NULL,
    revision TEXT NOT NULL
);

CREATE TABLE phase (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE procedure (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    name TEXT UNIQUE NOT NULL,
    pid TEXT UNIQUE NOT NULL
);

CREATE TABLE recipe (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    command_id INTEGER NOT NULL,
    instrument_id INTEGER NOT NULL,
    measurement_id INTEGER DEFAULT NULL,
    part_id INTEGER NOT NULL,
    phase_id INTEGER NOT NULL,
    procedure_id INTEGER NOT NULL,
    FOREIGN KEY(command_id) REFERENCES command(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(instrument_id) REFERENCES instrument(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(measurement_id) REFERENCES measurement(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(part_id) REFERENCES part(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(phase_id) REFERENCES phase(id) ON DELETE CASCADE ON UPDATE NO ACTION
    FOREIGN KEY(procedure_id) REFERENCES procedure(id) ON DELETE CASCADE ON UPDATE NO ACTION
);

CREATE TABLE setting (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT NULL,
    key TEXT UNIQUE NOT NULL,
    value TEXT NOT NULL
);

INSERT INTO setting (key, value) VALUES
    ("pattern", "(01)(?P<gtin>\d{14})(.*)(21)(?P<sn>\d{5})"),
    ("archive_url", "https://www.tofupilot.app/api/v1/runs"),
    ("archive_access_token", ""),
    ("password", "pbkdf2:sha256:260000$gtvpYNx6qtTuY8rt$2e2a4172758fee088e20d915ac4fdef3bdb07f792e42ecb2a77aa5a72bedd5f5");
