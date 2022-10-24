-- Add column in settings table for configuring the streaming mode of the remote
-- screen.

ALTER TABLE settings
    ADD COLUMN streaming_mode TEXT;
