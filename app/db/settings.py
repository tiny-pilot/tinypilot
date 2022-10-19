import db_connection

# We just store one collection of settings at a time, so the row id is fixed.
_ROW_ID = 1


class Settings:

    def __init__(self):
        self._db_connection = db_connection.get()

    def set_requires_https(self, should_be_required):
        self._db_connection.execute(
            'INSERT OR REPLACE INTO settings(id, requires_https)'
            ' VALUES (?, ?)', [_ROW_ID, should_be_required])

    def requires_https(self):
        """Retrieves the setting whether HTTPS connections are required.

        If there is no setting in the database, it defaults to True.

        Returns:
            bool.
        """
        cursor = self._db_connection.execute(
            'SELECT requires_https FROM settings WHERE id=?', [_ROW_ID])
        row = cursor.fetchone()
        if not row:
            return True
        return row[0] > 0  # Convert integer value to bool.
