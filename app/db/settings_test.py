import tempfile
import unittest
from unittest import mock

import db.settings
import db.store


class SettingsTest(unittest.TestCase):

    @mock.patch.object(db.settings, 'db_connection')
    def test_requires_https_by_default(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(temp_file.name)
            settings = db.settings.Settings()
            self.assertEqual(True, settings.requires_https())

    @mock.patch.object(db.settings, 'db_connection')
    def test_can_change_https_requirement(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(temp_file.name)
            settings = db.settings.Settings()
            settings.set_requires_https(False)
            self.assertEqual(False, settings.requires_https())

    @mock.patch.object(db.settings, 'db_connection')
    def test_reopening_connection_preserves_values(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(temp_file.name)
            settings = db.settings.Settings()
            settings.set_requires_https(False)
            settings = db.settings.Settings()  # Reopen the connection
            self.assertEqual(False, settings.requires_https())

    @mock.patch.object(db.settings, 'db_connection')
    def test_streamin_mode_default(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(temp_file.name)
            settings = db.settings.Settings()
            self.assertEqual(db.settings.StreamingMode.MJPEG, settings.get_streaming_mode())

    @mock.patch.object(db.settings, 'db_connection')
    def test_can_change_https_requirement(self, mock_db_connection):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_db_connection.get.return_value = db.store.create_or_open(temp_file.name)
            settings = db.settings.Settings()
            settings.set_streaming_mode(db.settings.StreamingMode.H264)
            self.assertEqual(db.settings.StreamingMode.H264, settings.get_streaming_mode())
