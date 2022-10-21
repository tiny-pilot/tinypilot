"""
For evolving our database schema over time, we follow the idea of “evolutionary
database design” (https://www.martinfowler.com/articles/evodb.html), which is
also used by DB migration tools like Liquibase or the one in Django.

The requirements for our app are rather simple, so instead of pulling in a
heavy-weight tool, we maintain our own mechanism. It is based off the exact same
philosophy, which is basically this:

- The database schema is defined through the linear sequence of migration
  statements. These are applied from the first to the last. After the last
  migration has run, the final schema is in place. We use the `_MIGRATIONS`
  list for storing all our migrations statements.
- Each migration step is applied atomically, i.e., inside a transaction – so
  it’s either effectuated completely, or not at all.
- The SQL code of a migration step must not perform its own transaction control
  (e.g., by issuing a `BEGIN` statement).
- The SQL code of a migration step may contain multiple SQL statements,
  delimited by a `;`.
- The incremental nature of this migration approach guarantees us that the
  entirety of all individual steps will always produce the exact same result,
  regardless of what initial version we start from. The downside is that we
  don’t see the final schema in the code directly.
- For keeping track of what migrations we have already run, we use SQlite’s
  `user_version` (https://www.sqlite.org/pragma.html#pragma_user_version)
  PRAGMA property. The value is effectively the count of migrations that have
  already been run, so a value of `3` means that the first 3 migrations from the
  `_MIGRATIONS` list have already been applied.
- Existing migration statements must be considered immutable, so you should only
  ever add new ones, but never modify existing statements. If you e.g. need to
  rollback something, you have to add a new migration that carries out the
  “inverse operation”. Contrary to other migration tools, we don’t write
  rollback procedures for every step, because our migrations are run
  automatically after the device had been updated. A rollback would require
  manual intervention, however. Therefore, it’s especially important to review
  and test every migration thoroughly.

Historical note: we didn’t have migrations right from the start, but we added
this functionality in January 2022. So for “old”/legacy databases it might occur
that the table structure of the first four migrations is already in place, but
the `user_version` property still has the initial value `0`. Nevertheless, it’s
always safe to run the first four migrations, because they are written in an
idempotent way. Once the migration mechanism was applied for the first time,
the database file is successfully converted to the “new” format, and from then
on it works the same everywhere.
"""
import glob
import logging
import os
import sqlite3

logger = logging.getLogger(__name__)

# Contains a list of SQL migration scripts in the order they should be applied.
# To avoid disk reads on every request, we store this in a module-level variable
# and lazy load it once.
_MIGRATIONS = None


def create_or_open(db_path):
    """Opens a connection to the database file.

    If there is no database file yet, it creates a new one on the fly. For
    existing database files, it automatically applies all pending schema
    migrations.

    Args:
        db_path: (str) Absolute path to the database file.

    Returns:
        (sqlite3.dbapi2.connection) Database connection object.
    """
    # We need a global to avoid re-reading the migrations on every request.
    # pylint: disable=global-statement
    global _MIGRATIONS

    logger.debug('reading SQLite databse from %s', db_path)
    connection = sqlite3.connect(db_path, isolation_level=None)

    # The `user_version` property tells us how many of the migrations were
    # already run in the past.
    cursor = connection.execute('PRAGMA user_version')
    initial_migrations_counter = cursor.fetchone()[0]

    if _MIGRATIONS is None:
        _MIGRATIONS = _load_migrations()

    if initial_migrations_counter == len(_MIGRATIONS):
        # TODO(jotaen) Remove this early return clause once we use a persistent
        #   database connection. Currently, this method is called on every
        #   single request, so it would pollute our logs.
        return connection

    logger.info('Migration counter: %s/%s (actual/total)',
                initial_migrations_counter, len(_MIGRATIONS))

    if initial_migrations_counter > len(_MIGRATIONS):
        # This case is very unlikely in practice. It might theoretically happen
        # if someone uses a recent version of a database with an older version
        # of the code. (E.g., if they have manually transferred a database file
        # to another device that is not running the latest code.)
        raise AssertionError('The database file is not compatible with the'
                             ' current version of the app.')

    for i in range(initial_migrations_counter, len(_MIGRATIONS)):
        # By using the connection object as context manager, sqlite3 will
        # automatically commit or rollback any ongoing transaction when exiting
        # the scope.
        with connection as transaction:
            # Without an explicit `BEGIN`, the sqlite3 library would autocommit
            # structural modifications immediately. See:
            # https://docs.python.org/3.7/library/sqlite3.html#transaction-control
            # Note that the `BEGIN` cannot be executed in a separate, preceding
            # `transaction.execute('BEGIN')` command, because
            # `transaction.executescript` automatically issues a `COMMIT` before
            # executing its script argument.
            transaction.executescript('BEGIN; ' + _MIGRATIONS[i])
            # SQlite doesn’t allow prepared statements for PRAGMA queries.
            # That’s okay here, since we know our query is safe.
            transaction.execute(f'PRAGMA user_version={i+1}')
        logger.info('Applied migration, counter is now at %d', i + 1)

    return connection


def _load_migrations():
    """Loads database migration SQL scripts from disk.

    Returns:
        A list of SQL scripts as strings, in the order they should be applied
        to bring the database to the correct state.
    """
    migrations_pattern = os.path.join(os.path.dirname(__file__), 'migrations',
                                      '*.sql')
    logger.debug('loading database migrations from %s', migrations_pattern)

    migrations = []
    for migration_script in sorted(glob.glob(migrations_pattern)):
        with open(migration_script, encoding='utf-8') as migration_file:
            migrations.append(migration_file.read())

    logger.debug('read %d database migrations from disk', len(migrations))

    return migrations
