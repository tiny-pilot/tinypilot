-- Create a table for storing TinyPilot license keys.

CREATE TABLE IF NOT EXISTS licenses(
    id INTEGER PRIMARY KEY,
    license_key TEXT NOT NULL
);
