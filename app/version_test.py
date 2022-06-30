import os
import tempfile
from unittest import TestCase
from unittest import mock

import version


class VersionTest(TestCase):

    def setUp(self):
        # Run all unit tests with debug mode disabled.
        is_debug_patch = mock.patch.object(version,
                                           '_is_debug',
                                           return_value=False)
        self.addCleanup(is_debug_patch.stop)
        is_debug_patch.start()

    def test_local_version_returns_dummy_version_when_in_debug_mode(self):
        # Enable debug mode.
        with mock.patch.object(version, '_is_debug', return_value=True):
            self.assertEqual('0000000', version.local_version())

    def test_local_version_when_file_exists(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('1234567')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                self.assertEqual('1234567', version.local_version())

    def test_local_version_strips_leading_trailing_whitespace(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('    1234567   \n')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                self.assertEqual('1234567', version.local_version())

    def test_local_version_raises_file_error_when_file_doesnt_exist(self):
        with tempfile.TemporaryDirectory() as mock_version_dir:
            mock_version_file_name = os.path.join(mock_version_dir,
                                                  'version-file')

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file_name):
                with self.assertRaises(version.FileError):
                    version.local_version()
