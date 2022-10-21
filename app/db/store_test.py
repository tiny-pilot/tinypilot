import sqlite3
import tempfile
import unittest
from unittest import mock

import db.store


def all_tables(connection):
    """Returns all table names as list of strings."""
    cursor = connection.execute("""
        SELECT name FROM sqlite_master
        WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
    """)
    return [row[0] for row in cursor.fetchall()]


def migrations_counter(connection):
    """Returns the migrations counter as int."""
    cursor = connection.execute('PRAGMA user_version')
    return cursor.fetchone()[0]


class StoreTest(unittest.TestCase):

    @mock.patch('db.store._load_migrations', [
        'CREATE TABLE first(id INTEGER)',
        'CREATE TABLE second(id INTEGER)',
    ])
    def test_applies_migrations_and_adjusts_migration_counter_on_initialization(
            self):
        with tempfile.NamedTemporaryFile() as temp_file:
            connection = db.store.create_or_open(temp_file.name)
            self.assertEqual(['first', 'second'], all_tables(connection))
            self.assertEqual(2, migrations_counter(connection))

    @mock.patch('db.store._load_migrations', [
        'CREATE TABLE first(id INTEGER); CREATE TABLE second(id INTEGER)',
    ])
    def test_processes_multistatement_migrations(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            connection = db.store.create_or_open(temp_file.name)
            self.assertEqual(['first', 'second'], all_tables(connection))
            self.assertEqual(1, migrations_counter(connection))

    @mock.patch('db.store._load_migrations', [])
    def test_noop_if_no_migrations_are_specified(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            connection = db.store.create_or_open(temp_file.name)
            self.assertEqual(0, migrations_counter(connection))

    def test_applies_migrations_on_initialization(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            # First, run the initial migrations.
            with mock.patch('db.store._load_migrations', [
                    'CREATE TABLE first(id INTEGER)',
                    'CREATE TABLE third(id INTEGER)',
                    'ALTER TABLE third RENAME TO second',
            ]):
                connection = db.store.create_or_open(temp_file.name)
                self.assertEqual(3, migrations_counter(connection))
                self.assertEqual(['first', 'second'], all_tables(connection))

            # Then, add a new migration to the list and re-initialize the DB.
            with mock.patch(
                    'db.store._load_migrations',
                [
                    'CREATE TABLE first(id INTEGER)',
                    'CREATE TABLE third(id INTEGER)',
                    'ALTER TABLE third RENAME TO second',
                    'CREATE TABLE third(id INTEGER)',  # <-- this one is new
                ]):
                connection = db.store.create_or_open(temp_file.name)
                self.assertEqual(4, migrations_counter(connection))
                self.assertEqual(['first', 'second', 'third'],
                                 all_tables(connection))

    @mock.patch('db.store._load_migrations', [
        'CREATE TABLE first(id INTEGER)',
        'CREATE TABLE second(id INTEGER)',
    ])
    def test_disregards_previously_existing_structure(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            # Set up a database manually and initialize it with a schema.
            connection1 = sqlite3.connect(temp_file.name, isolation_level=None)
            connection1.execute('CREATE TABLE zero(id INTEGER)')

            # Now, open that same database through our migration manager. Since
            # the migrations don’t logically conflict with the previous schema,
            # it just applies the migrations and leaves the previous schema
            # intact.
            connection2 = db.store.create_or_open(temp_file.name)
            self.assertEqual(['zero', 'first', 'second'],
                             all_tables(connection2))
            self.assertEqual(2, migrations_counter(connection2))

    @mock.patch('db.store._load_migrations', [
        'CREATE TABLE first(id INTEGER)',
        'CREATE TABLE second(id INTEGER)',
    ])
    def test_does_not_run_migrations_redundantly(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            # Opening the file for the first time applies all migrations.
            connection1 = db.store.create_or_open(temp_file.name)
            self.assertEqual(2, migrations_counter(connection1))

            # Now, open the same file once again. This time, it should skip
            # all migrations. (If it didn’t, this would raise SQL errors.)
            connection2 = db.store.create_or_open(temp_file.name)
            self.assertEqual(2, migrations_counter(connection2))

    @mock.patch(
        'db.store._load_migrations',
        [
            'CREATE TABLE first(id INTEGER)',
            # The next statement will fail, since table `first` already exists.
            'CREATE TABLE first(name TEXT)',
            'CREATE TABLE second(id INTEGER)',
        ])
    def test_aborts_on_bad_migration(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            with self.assertRaises(sqlite3.OperationalError):
                db.store.create_or_open(temp_file.name)

            connection = sqlite3.connect(temp_file.name, isolation_level=None)

            # The migration is supposed to be aborted on first error, and the
            # state of the last successful migration should be effective.
            self.assertEqual(1, migrations_counter(connection))
            self.assertEqual(['first'], all_tables(connection))

    @mock.patch(
        'db.store._load_migrations',
        [
            'CREATE TABLE first(id INTEGER)',
            # The next statement will fail, since it tries to create table
            # `second` two times, which is not possible.
            'CREATE TABLE second(name TEXT); CREATE TABLE second(name INTEGER)',
        ])
    def test_executes_multistatement_migration_atomically(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            with self.assertRaises(sqlite3.OperationalError):
                db.store.create_or_open(temp_file.name)

            connection = sqlite3.connect(temp_file.name, isolation_level=None)

            # The multi-statement migration must be atomic – so instead of it
            # being partially applied, it should be rolled backed altogether.
            self.assertEqual(1, migrations_counter(connection))
            self.assertEqual(['first'], all_tables(connection))

    @mock.patch('db.store._load_migrations', ['CREATE TABLE first(id INTEGER)'])
    def test_aborts_if_migration_counter_is_incompatible(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            connection = sqlite3.connect(temp_file.name, isolation_level=None)
            connection.execute('PRAGMA user_version=2')

            # The `user_version` can’t be greater than 1, because there is just
            # a single migration defined.
            with self.assertRaises(AssertionError):
                db.store.create_or_open(temp_file.name)
