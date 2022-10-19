import datetime
import sqlite3

import db_connection


class Error(Exception):
    pass


class UserAlreadyExistsError(Error):
    pass


class UserDoesNotExistError(Error):
    pass


class Users:

    def __init__(self):
        self._db_connection = db_connection.get()

    def add(self, username, password_hash, credentials_change_time):
        try:
            self._db_connection.execute(
                'INSERT'
                ' INTO users(username, password_hash, credentials_last_changed)'
                ' VALUES (?, ?, ?)', [
                    username, password_hash,
                    _to_iso_string(credentials_change_time)
                ])
        except sqlite3.IntegrityError as e:
            raise UserAlreadyExistsError(
                f'User already exists: {username}') from e

    def change_password(self, username, new_password_hash,
                        credentials_change_time):
        cursor = self._db_connection.execute(
            'UPDATE users'
            ' SET password_hash = ?, credentials_last_changed = ?'
            ' WHERE username = ?', [
                new_password_hash,
                _to_iso_string(credentials_change_time), username
            ])
        if cursor.rowcount == 0:
            raise UserDoesNotExistError(f'User does not exist: {username}')

    def delete(self, username):
        cursor = self._db_connection.execute(
            'DELETE FROM users WHERE username = ?', [username])
        if cursor.rowcount == 0:
            raise UserDoesNotExistError(f'User does not exist: {username}')

    def delete_all(self):
        self._db_connection.execute('DELETE FROM users')

    def get_all(self):
        cursor = self._db_connection.execute(
            'SELECT username FROM users ORDER BY id')
        users = [u[0] for u in cursor.fetchall()]
        return users

    def get_password_hash(self, username):
        cursor = self._db_connection.execute(
            'SELECT password_hash FROM users WHERE username=? LIMIT 1',
            [username])
        row = cursor.fetchone()
        if not row:
            return None
        return row[0]

    def get_credentials_last_changed(self, username):
        cursor = self._db_connection.execute(
            'SELECT credentials_last_changed'
            ' FROM users WHERE username=? LIMIT 1', [username])
        row = cursor.fetchone()
        if not row:
            return None
        return datetime.datetime.fromisoformat(row[0])


def _to_iso_string(timestamp):
    """Returns the timestamp (datetime.datetime) as ISO8601 formatted string."""
    # Without `timespec='microseconds`, the `isoformat` function would truncate
    # the fractional seconds part if it’s zero. However, we store timestamps
    # as plain strings in the database, so that inconsistent serialization
    # behaviour would make it tricky to perform queries on that value.
    # E.g.: 2000-01-01T00:00:00.000000 and 2000-01-01T00:00:00 are logically
    # equal, but a text-based comparison would fail.
    return timestamp.isoformat(timespec='microseconds')
