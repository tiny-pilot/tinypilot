-- Add column for storing the relative/absolute mouse mode setting.

ALTER TABLE settings
ADD COLUMN mouse_mode TEXT NOT NULL DEFAULT 'ABSOLUTE';
