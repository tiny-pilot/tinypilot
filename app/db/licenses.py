import db_connection

# We store one license key at a time, per license level.


class Error(Exception):
    pass


class NoLicenseStoredError(Error):
    code = 'NO_LICENSE_STORED'


class Licenses:

    def __init__(self):
        self._db_connection = db_connection.get()

    def save(self, license_key, license_level):
        self._db_connection.execute(
            'INSERT OR REPLACE INTO licenses(license_key, license_level)'
            ' VALUES (?, ?)', [license_key, license_level])

    def get(self, license_level):
        cursor = self._db_connection.execute(
            'SELECT license_key FROM licenses WHERE license_level = ?',
            [license_level])
        row = cursor.fetchone()
        if not row:
            raise NoLicenseStoredError(
                f'There is no {license_level} license stored')
        return row[0]

    def delete(self, license_level):
        cursor = self._db_connection.execute(
            'DELETE FROM licenses WHERE license_level = ?', [license_level])
        if cursor.rowcount == 0:
            raise NoLicenseStoredError(
                f'There is no {license_level} license stored')
