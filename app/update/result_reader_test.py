import datetime
import os
import tempfile
import unittest
from unittest import mock

import update.result
import update.result_reader


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

    @mock.patch.object(update.result_reader.glob, 'glob')
    def test_returns_none_when_no_result_files_exist(self, mock_glob):
        mock_glob.return_value = []
        self.assertIsNone(update.result_reader.read())

    @mock.patch.object(update.result_reader.glob, 'glob')
    @mock.patch.object(update.result_reader.utc, 'now')
    def test_returns_latest_if_it_is_within_last_eight_minutes(
            self, mock_now, mock_glob):
        mock_glob.return_value = [
            self.make_mock_file(
                '2020-12-31T000000Z-update-result.json', """
{
  "error": "",
  "timestamp": "2020-12-31T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000000Z-update-result.json', """
{
  "error": "",
  "timestamp": "2021-01-01T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000300Z-update-result.json', """
{
  "error": "",
  "timestamp": "2021-01-01T000300Z"
}
            """)
        ]
        mock_now.return_value = datetime.datetime(year=2021,
                                                  month=1,
                                                  day=1,
                                                  hour=0,
                                                  minute=5,
                                                  second=0,
                                                  tzinfo=datetime.timezone.utc)
        self.assertEqual(
            update.result.Result(error='',
                                 timestamp=datetime.datetime(
                                     year=2021,
                                     month=1,
                                     day=1,
                                     hour=0,
                                     minute=3,
                                     second=0,
                                     tzinfo=datetime.timezone.utc)),
            update.result_reader.read())

    @mock.patch.object(update.result_reader.glob, 'glob')
    @mock.patch.object(update.result_reader.utc, 'now')
    def test_returns_latest_if_it_is_in_the_future(self, mock_now, mock_glob):
        """Due to NTP updates, the latest result might be from a later time."""
        mock_glob.return_value = [
            self.make_mock_file(
                '2021-01-01T000000Z-update-result.json', """
{
  "error": "",
  "timestamp": "2021-01-01T000000Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000300Z-update-result.json', """
{
  "error": "",
  "timestamp": "2021-01-01T000300Z"
}
            """),
            self.make_mock_file(
                '2021-01-01T000600Z-update-result.json', """
{
  "error": "",
  "timestamp": "2021-01-01T000600Z"
}
            """)
        ]
        # Set the current time to one minute *behind* the latest result
        # timestamp to simulate a time adjustment after, e.g., an NTP update.
        mock_now.return_value = datetime.datetime(year=2021,
                                                  month=1,
                                                  day=1,
                                                  hour=0,
                                                  minute=5,
                                                  second=0,
                                                  tzinfo=datetime.timezone.utc)
        self.assertEqual(
            update.result.Result(error='',
                                 timestamp=datetime.datetime(
                                     year=2021,
                                     month=1,
                                     day=1,
                                     hour=0,
                                     minute=6,
                                     second=0,
                                     tzinfo=datetime.timezone.utc)),
            update.result_reader.read())

    @mock.patch.object(update.result_reader.glob, 'glob')
    @mock.patch.object(update.result_reader.utc, 'now')
    def test_returns_none_if_all_results_are_older_than_eight_minutes(
            self, mock_now, mock_glob):
        mock_glob.return_value = [
            self.make_mock_file(
                '2021-01-01T000000Z', """
{
  "error": "",
  "timestamp": "2021-01-01T000000Z"
}
            """)
        ]
        # Set current time to be 8m01s after most recent result.
        mock_now.return_value = datetime.datetime(year=2021,
                                                  month=1,
                                                  day=1,
                                                  hour=0,
                                                  minute=8,
                                                  second=1,
                                                  tzinfo=datetime.timezone.utc)
        self.assertIsNone(update.result_reader.read())
