-- Create a table for storing serial terminal settings.

CREATE TABLE IF NOT EXISTS serial_terminal(
    id INTEGER PRIMARY KEY,
    port TEXT NOT NULL UNIQUE,
    baud_rate INTEGER NOT NULL,
    data_bits INTEGER NOT NULL,
    stop_bits INTEGER NOT NULL,
    parity TEXT NOT NULL,
    flow_control TEXT NOT NULL
);
