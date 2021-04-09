import datetime
import os
import tempfile
import unittest
from unittest import mock

import update_result
import update_result_reader


class UpdateResultReaderTest(unittest.TestCase):

    def setUp(self):
        self.mock_result_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.mock_result_dir.cleanup()

    def make_mock_file(self, filename, contents):
        full_path = os.path.join(self.mock_result_dir.name, filename)
        with open(full_path, 'w') as mock_file:
            mock_file.write(contents)
        return full_path

    @mock.patch.object(update_result_reader.glob, 'glob')
    def test_returns_none_when_no_result_files_exist(self, mock_glob):
        mock_glob.return_value = []
        self.assertIsNone(update_result_reader.read())

    @mock.patch.object(update_result_reader.glob, 'glob')
    @mock.patch.object(update_result_reader.utc, 'now')
    def test_returns_latest(self, mock_now, mock_glob):
        mock_glob.return_value = [
            self.make_mock_file(
                'foo.json', """
{
  "success": true,
  "error": "",
  "timestamp": "2021-02-10T085735Z"
}
            """)
        ]
        mock_now.return_value = datetime.datetime(2021,
                                                  2,
                                                  10,
                                                  8,
                                                  57,
                                                  36,
                                                  tzinfo=datetime.timezone.utc)
        self.assertEqual(
            update_result.Result(success=True,
                                 error='',
                                 timestamp=datetime.datetime(
                                     2021,
                                     2,
                                     10,
                                     8,
                                     57,
                                     35,
                                     tzinfo=datetime.timezone.utc)),
            update_result_reader.read())
