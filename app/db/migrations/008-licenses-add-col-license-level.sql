-- Add license_level column to licenses table to be able to store different
-- types of licenses. For example, storing both an Enterprise license and a Pro
-- license.

-- Note: The default value is only there to populate existing records.
ALTER TABLE licenses
ADD COLUMN license_level TEXT NOT NULL DEFAULT 'ENTERPRISE';

-- Ensure that only a single license of each type can be stored.
CREATE UNIQUE INDEX IF NOT EXISTS idx_licenses_license_level
ON licenses(license_level);
