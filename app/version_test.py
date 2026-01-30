import io
import json
import tempfile
import urllib.error
import urllib.request
from unittest import TestCase
from unittest import mock

import version


class LocalVersionTest(TestCase):

    def setUp(self):
        # Run all unit tests with debug mode disabled.
        is_debug_patch = mock.patch.object(version,
                                           '_is_debug',
                                           return_value=False)
        self.addCleanup(is_debug_patch.stop)
        is_debug_patch.start()

    def test_local_version_when_file_exists(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('1.2.3-16+7a6c812')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                self.assertEqual('1.2.3-16+7a6c812', version.local_version())

    def test_local_version_strips_leading_trailing_whitespace(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:
            mock_version_file.write('    1.2.3-16+7a6c812   \n')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                self.assertEqual('1.2.3-16+7a6c812', version.local_version())

    def test_local_version_raises_file_error_when_file_doesnt_exist(self):
        with mock.patch.object(version, '_VERSION_FILE',
                               'non-existent-file.txt'):
            with self.assertRaises(version.VersionFileError):
                version.local_version()

    def test_local_version_raises_file_error_when_file_is_empty(self):
        with tempfile.NamedTemporaryFile('w',
                                         encoding='utf-8') as mock_version_file:

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                with self.assertRaises(version.VersionFileError):
                    version.local_version()

    def test_local_version_raises_file_error_when_file_is_not_utf_8(self):
        with tempfile.NamedTemporaryFile() as mock_version_file:
            mock_version_file.write(b'\xff')
            mock_version_file.flush()

            with mock.patch.object(version, '_VERSION_FILE',
                                   mock_version_file.name):
                with self.assertRaises(version.VersionFileError):
                    version.local_version()


class LatestVersionTest(TestCase):

    def setUp(self):
        # Run all unit tests with version's debug mode enabled.
        version_is_debug_patch = mock.patch.object(version,
                                                   '_is_debug',
                                                   return_value=True)
        self.addCleanup(version_is_debug_patch.stop)
        version_is_debug_patch.start()

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_when_request_is_successful(self, mock_urlopen):
        mock_response = mock.Mock()
        mock_response.read.return_value = json.dumps({
            'version': '1.2.3-16+7a6c812',
            'kind': 'automatic',
            'data': None,
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertEqual('1.2.3-16+7a6c812', version.latest_version().version)
        self.assertEqual('automatic', version.latest_version().kind)
        self.assertEqual(None, version.latest_version().data)

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_raises_request_error_when_response_is_not_utf_8(
            self, mock_urlopen):
        mock_response = mock.Mock()
        mock_response.read.return_value = b'\xff'
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(version.VersionRequestError):
            version.latest_version()

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_raises_request_error_when_response_is_not_json(
            self, mock_urlopen):
        mock_response = mock.Mock()
        mock_response.read.return_value = 'plain text'.encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(version.VersionRequestError):
            version.latest_version()

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_raises_request_error_when_response_is_not_json_dict(
            self, mock_urlopen):
        mock_response = mock.Mock()
        mock_response.read.return_value = json.dumps(
            'json encoded string').encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(version.VersionRequestError):
            version.latest_version()

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_raises_request_error_when_response_missing_field(
            self, mock_urlopen):
        mock_response = mock.Mock()
        mock_response.read.return_value = json.dumps({
            'wrong_field_name': 'wrong_field_value'
        }).encode('utf-8')
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaises(version.VersionRequestError):
            version.latest_version()

    @mock.patch.object(urllib.request, 'urlopen')
    def test_latest_version_raises_request_error_when_request_fails(
            self, mock_urlopen):
        urlopen_mock = mock.Mock(side_effect=urllib.error.HTTPError(
            '127.0.0.1', 400, '400 Bad Request', None, io.BytesIO(
                b'bad request')))
        mock_urlopen.return_value.__enter__ = urlopen_mock

        with self.assertRaises(version.VersionRequestError) as ctx:
            version.latest_version()

        self.assertEqual(
            'Failed to request latest available version: bad request',
            str(ctx.exception))


class DebugModeLocalVersionTest(TestCase):

    def test_local_version_returns_dummy_version_when_in_debug_mode(self):
        # Enable debug mode.
        with mock.patch.object(version, '_is_debug', return_value=True):
            self.assertEqual('0.0.0-0+aaaaaaa', version.local_version())
