import db_connection

# At the moment, we store a single MAC address only, so the id is fixed.
_ROW_ID = 1


class WakeOnLan:

    def __init__(self):
        self._db_connection = db_connection.get()

    def save(self, normalized_mac_address):
        self._db_connection.execute(
            'INSERT OR REPLACE INTO wake_on_lan(id, mac_address) VALUES (?, ?)',
            [_ROW_ID, normalized_mac_address])

    def get(self):
        cursor = self._db_connection.execute(
            'SELECT mac_address FROM wake_on_lan WHERE id=?', [_ROW_ID])
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

    def clear(self):
        self._db_connection.execute('DELETE FROM wake_on_lan')
