import tempfile
import unittest
from unittest import mock

import db.settings
import db.store


class SettingsTest(unittest.TestCase):

    # We need this test to make sure that the initialization procedure in the
    # `Settings` constructor doesn’t mess with existing data.
    @mock.patch.object(db.settings, 'db_connection')
    def test_preserves_data_across_connections(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(
                temp_file.name)
            settings = db.settings.Settings()
            initial_value = settings.requires_https()
            settings.set_requires_https(not initial_value)

            # Re-initialize and query again.
            settings = db.settings.Settings()
            self.assertEqual(not initial_value, settings.requires_https())

    @mock.patch.object(db.settings, 'db_connection')
    def test_requires_https_by_default(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(
                temp_file.name)
            settings = db.settings.Settings()
            self.assertEqual(True, settings.requires_https())

    @mock.patch.object(db.settings, 'db_connection')
    def test_can_change_https_requirement(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(
                temp_file.name)
            settings = db.settings.Settings()
            settings.set_requires_https(False)
            self.assertEqual(False, settings.requires_https())
