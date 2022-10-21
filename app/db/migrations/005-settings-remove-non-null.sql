-- Remove non-null constraint from settings table (see explanation in
-- `settings.py`). Since sqlite doesn’t natively support that operation, we
--  have to use an intermediate table.

CREATE TABLE __settings__(
    id INTEGER PRIMARY KEY,
    requires_https INTEGER
);
INSERT INTO __settings__ SELECT * FROM settings;
DROP TABLE settings;
ALTER TABLE __settings__ RENAME TO settings;
