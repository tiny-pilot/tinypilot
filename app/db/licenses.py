import db_connection

# We just store one license key at a time, so the row id is fixed.
_ROW_ID = 1


class Licenses:

    def __init__(self):
        self._db_connection = db_connection.get()

    def save(self, license_key):
        self._db_connection.execute(
            'INSERT OR REPLACE INTO licenses(id, license_key) VALUES (?, ?)',
            [_ROW_ID, license_key])

    def get(self):
        cursor = self._db_connection.execute(
            'SELECT license_key FROM licenses WHERE id=?', [_ROW_ID])
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]
