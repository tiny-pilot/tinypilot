import flask

import db.store
import env

_DB_PATH = env.abs_path_in_home_dir('tinypilot.db')


def get():
    """Returns a database connection (sqlite3.dbapi2.connection)."""
    # Keep in mind that Flask only caches the connection object on a per-request
    # basis, and not throughout the entire runtime of the server.
    connection = _get_flask_db()
    if connection is None:
        connection = db.store.create_or_open(_DB_PATH)
        _set_flask_db(connection)
    return connection


def close():
    connection = _get_flask_db()
    if connection is not None:
        connection.close()


def _get_flask_db():
    return getattr(flask.g, '_database', None)


def _set_flask_db(flask_db):
    flask.g._database = flask_db  # pylint: disable=protected-access
