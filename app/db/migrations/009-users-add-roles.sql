-- Add column for user roles.
-- Any previously existing users have `ADMIN` role.
-- Note that the name `role` is a reserved identifier in SQL. We therefore use
-- `auth_role` as column name, to avoid potential ambiguities.

ALTER TABLE users
ADD COLUMN auth_role TEXT NOT NULL DEFAULT 'ADMIN';
