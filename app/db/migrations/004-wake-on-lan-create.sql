-- Create a table for storing wake on LAN target addresses.

CREATE TABLE IF NOT EXISTS wake_on_lan(
    id INTEGER PRIMARY KEY,
    mac_address TEXT NOT NULL UNIQUE
    );
