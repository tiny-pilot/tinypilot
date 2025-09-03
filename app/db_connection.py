import flask

import db.store
import env

_DB_PATH = env.abs_path_in_home_dir('tinypilot.db')


def get():
    """Returns a connection to the SQlite database.

    Within a Flask app context, this function applies a caching mechanism to
    avoid redundant initialization overhead. Outside a Flask app context, it
    creates a fresh DB connection on every invocation.

    Returns:
        sqlite3.dbapi2.connection
    """
    if not flask.has_app_context():
        return db.store.create_or_open(_DB_PATH)

    connection = _get_cached_flask_db()
    if connection is None:
        connection = db.store.create_or_open(_DB_PATH)
        _cache_flask_db(connection)
    return connection


def close():
    """Closes a potentially cached DB connection.

    Noop if no DB connection was cached or if invocation context is not within
    Flask.
    """
    if not flask.has_app_context():
        return

    connection = _get_cached_flask_db()
    if connection is not None:
        connection.close()


def _get_cached_flask_db():
    return getattr(flask.g, '_database', None)


def _cache_flask_db(flask_db):
    flask.g._database = flask_db  # pylint: disable=protected-access
