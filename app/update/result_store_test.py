import datetime
import os
import tempfile
import unittest
from unittest import mock

import update.result
import update.result_store


class ResultStoreReadTest(unittest.TestCase):

    def setUp(self):
        self.mock_result_dir = tempfile.TemporaryDirectory()

        result_path_patch = mock.patch.object(
            update.result_store, '_RESULT_PATH',
            os.path.join(self.mock_result_dir.name,
                         'latest-update-result.json'))
        self.addCleanup(result_path_patch.stop)
        result_path_patch.start()

    def tearDown(self):
        self.mock_result_dir.cleanup()

    def make_mock_file(self, filename, contents):
        full_path = os.path.join(self.mock_result_dir.name, filename)
        with open(full_path, 'w') as mock_file:
            mock_file.write(contents)
        return full_path

    @mock.patch.object(update.result_store.glob, 'glob')
    def test_returns_none_when_no_result_files_exist(self, mock_glob):
        mock_glob.return_value = []
        self.assertIsNone(update.result_store.read())

    @mock.patch.object(update.result_store.glob, 'glob')
    def test_returns_value_from_result_file(self, mock_glob):
        mock_glob.return_value = [
            self.make_mock_file(
                'latest-update-result.json', """
{
  "error": null,
  "timestamp": "2021-01-01T000300Z"
}
            """)
        ]
        self.assertEqual(
            update.result.Result(error=None,
                                 timestamp=datetime.datetime(
                                     year=2021,
                                     month=1,
                                     day=1,
                                     hour=0,
                                     minute=3,
                                     second=0,
                                     tzinfo=datetime.timezone.utc)),
            update.result_store.read())
        # result_store.read shouldn't have checked for legacy result files.
        mock_glob.assert_not_called()

    @mock.patch.object(update.result_store.glob, 'glob')
    def test_returns_latest_legacy_result(self, mock_glob):
        mock_glob.return_value = [
            self.make_mock_file(
                '2020-12-31T000000Z-update-result.json', """
{
  "error": null,
  "timestamp": "2020-12-31T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000000Z-update-result.json', """
{
  "error": null,
  "timestamp": "2021-01-01T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000300Z-update-result.json', """
{
  "error": null,
  "timestamp": "2021-01-01T000300Z"
}
            """)
        ]
        self.assertEqual(
            update.result.Result(error=None,
                                 timestamp=datetime.datetime(
                                     year=2021,
                                     month=1,
                                     day=1,
                                     hour=0,
                                     minute=3,
                                     second=0,
                                     tzinfo=datetime.timezone.utc)),
            update.result_store.read())


class ResultStoreClearTest(unittest.TestCase):

    def setUp(self):
        self.mock_result_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.mock_result_dir.cleanup()

    def make_mock_file(self, filename, contents):
        full_path = os.path.join(self.mock_result_dir.name, filename)
        with open(full_path, 'w') as mock_file:
            mock_file.write(contents)
        return full_path

    @mock.patch.object(update.result_store.os, 'remove')
    @mock.patch.object(update.result_store.glob, 'glob')
    def test_removes_result_file(self, mock_glob, mock_remove):
        mock_file_paths = [
            self.make_mock_file(
                'latest-update-result.json', """
{
  "error": null,
  "timestamp": "2020-12-31T000000Z"
}
            """)
        ]
        mock_glob.return_value = mock_file_paths
        update.result_store.clear()
        mock_remove.assert_has_calls([
            mock.call(mock_file_paths[0]),
        ])

    @mock.patch.object(update.result_store.os, 'remove')
    @mock.patch.object(update.result_store.glob, 'glob')
    def test_removes_legacy_files(self, mock_glob, mock_remove):
        mock_file_paths = [
            self.make_mock_file(
                '2020-12-31T000000Z-update-result.json', """
{
  "error": null,
  "timestamp": "2020-12-31T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000000Z-update-result.json', """
{
  "error": null,
  "timestamp": "2021-01-01T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000300Z-update-result.json', """
{
  "error": null,
  "timestamp": "2021-01-01T000300Z"
}
            """)
        ]
        mock_glob.return_value = mock_file_paths
        update.result_store.clear()
        mock_remove.assert_has_calls([
            mock.call(mock_file_paths[0]),
            mock.call(mock_file_paths[1]),
            mock.call(mock_file_paths[2]),
        ])

    # pylint incorrectly complains that this could be a free function, but it
    # needs to be part of unittest.TestCase.
    # pylint: disable=no-self-use
    @mock.patch.object(update.result_store.os, 'remove')
    @mock.patch.object(update.result_store.glob, 'glob')
    def test_clear_does_nothing_when_no_result_files_exist(
            self, mock_glob, mock_remove):
        mock_glob.return_value = []

        update.result_store.clear()

        mock_remove.assert_not_called()


class ResultStoreWriteTest(unittest.TestCase):

    def setUp(self):
        self.mock_result_dir = tempfile.TemporaryDirectory()

        result_dir_patch = mock.patch.object(update.result_store,
                                             '_RESULT_FILE_DIR',
                                             self.mock_result_dir.name)
        self.addCleanup(result_dir_patch.stop)
        result_dir_patch.start()

        result_path_patch = mock.patch.object(
            update.result_store, '_RESULT_PATH',
            os.path.join(self.mock_result_dir.name,
                         'latest-update-result.json'))
        self.addCleanup(result_path_patch.stop)
        result_path_patch.start()

    def tearDown(self):
        self.mock_result_dir.cleanup()

    def read_result_file(self, result_filename):
        full_path = os.path.join(self.mock_result_dir.name, result_filename)
        with open(full_path) as result_file:
            return result_file.read()

    def test_writes_result_accurately(self):
        update.result_store.write(
            update.result.Result(error=None,
                                 timestamp=datetime.datetime(
                                     year=2021,
                                     month=2,
                                     day=3,
                                     hour=4,
                                     minute=5,
                                     second=6,
                                     tzinfo=datetime.timezone.utc)))
        self.assertEqual('{"error": null, "timestamp": "2021-02-03T040506Z"}',
                         self.read_result_file('latest-update-result.json'))
