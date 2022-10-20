import enum

import db_connection

# We just store one collection of settings at a time, so the row id is fixed.
_ROW_ID = 1


class StreamingMode(enum.Enum):
    MJPEG = 'MJPEG'
    H264 = 'H264'


class Settings:
    # The columns of the settings table should never have a `NON NULL`
    # constraint, otherwise it wouldn’t be possible to selectively set or update
    # individual columns.

    def __init__(self):
        self._db_connection = db_connection.get()
        # Initialize the table by making sure the “hard-coded” row exists.
        self._db_connection.execute(
            'INSERT OR IGNORE INTO settings(id) VALUES (?)', [_ROW_ID])

    def set_requires_https(self, should_be_required):
        self._db_connection.execute(
            'UPDATE settings SET requires_https=? WHERE id=?',
            [should_be_required, _ROW_ID])

    def requires_https(self):
        """Retrieves the setting whether HTTPS connections are required.

        If there is no setting in the database, it defaults to True.

        Returns:
            bool.
        """
        cursor = self._db_connection.execute(
            'SELECT requires_https FROM settings WHERE id=?', [_ROW_ID])
        # Reminder: the `requires_https` column is of type integer.
        raw_value = _fetch_single_value(cursor, 1)
        return raw_value > 0  # Convert integer value to bool.

    def get_streaming_mode(self):
        """Retrieves the preferred streaming mode for the remote screen.

        Returns:
            A `StreamingMode` value.
        """
        cursor = self._db_connection.execute(
            'SELECT streaming_mode FROM settings WHERE id=?', [_ROW_ID])
        raw_value = _fetch_single_value(cursor, StreamingMode.MJPEG.value)
        return StreamingMode(raw_value)

    def set_streaming_mode(self, streaming_mode):
        """Stores the preferred streaming mode.

        Args:
            streaming_mode: `StreamingMode` value.
        """
        self._db_connection.execute(
            'UPDATE settings SET streaming_mode=? WHERE id=?',
            [streaming_mode.value, _ROW_ID])


def _fetch_single_value(connection_cursor, default_value):
    """Helper method to resolve a query for one single value."""
    row = connection_cursor.fetchone()
    if not row or row[0] is None:
        return default_value
    return row[0]
