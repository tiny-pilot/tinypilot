import os
import tempfile
from unittest import TestCase
from unittest import mock

import version


class VersionTest(TestCase):

    def test_local_version_returns_dummy_version_when_in_debug_mode(self):
        with mock.patch.object(version, '_is_debug', return_value=True):
            self.assertEqual('0000000', version.local_version())

    def test_local_version_when_file_exists(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('1234567')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name), mock.patch.object(
                                       version, '_is_debug',
                                       return_value=False):
                self.assertEqual('1234567', version.local_version())

    def test_local_version_strips_leading_trailing_whitespace(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('    1234567   \n')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name), mock.patch.object(
                                       version, '_is_debug',
                                       return_value=False):
                self.assertEqual('1234567', version.local_version())

    def test_local_version_raises_file_error_when_file_doesnt_exist(self):
        with tempfile.TemporaryDirectory() as mock_version_dir:
            mock_version_file_name = os.path.join(mock_version_dir,
                                                  'version-file')

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file_name), mock.patch.object(
                                       version, '_is_debug',
                                       return_value=False):
                with self.assertRaises(version.FileError):
                    version.local_version()
