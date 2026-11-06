-- Add column in settings table for configuring whether to invert the scroll
-- direction of the mouse wheel.

ALTER TABLE settings
ADD COLUMN invert_scroll_direction INTEGER;
