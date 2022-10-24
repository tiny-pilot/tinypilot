-- Create a table for storing TinyPilot runtime settings.

CREATE TABLE IF NOT EXISTS settings(
    id INTEGER PRIMARY KEY,
    requires_https INTEGER NOT NULL
    );
