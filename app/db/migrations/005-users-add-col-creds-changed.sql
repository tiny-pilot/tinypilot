-- Add column for keeping track of when credentials were changed. The default
-- value is only needed for previously existing rows.

ALTER TABLE users
    ADD COLUMN credentials_last_changed
    TEXT NOT NULL DEFAULT "0001-01-01T00:00:00.000000+00:00";
