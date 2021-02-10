import datetime
import io
import unittest

import update_result


class UpdateResultTest(unittest.TestCase):

    def test_reads_correct_values_for_successful_result(self):
        mock_file = io.StringIO("""
{
  "success": true,
  "error": "",
  "timestamp": "2021-02-10T085735Z"
}
""")
        self.assertEqual(
            update_result.Result(
                success=True,
                error='',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), update_result.read(mock_file))

    def test_reads_correct_values_for_failed_result(self):
        mock_file = io.StringIO("""
{
  "success": false,
  "error": "dummy update error",
  "timestamp": "2021-02-10T085735Z"
}
""")
        self.assertEqual(
            update_result.Result(
                success=False,
                error='dummy update error',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), update_result.read(mock_file))

    def test_reads_default_values_for_empty_dict(self):
        mock_file = io.StringIO('{}')
        self.assertEqual(
            update_result.Result(
                success=False,
                error='',
                timestamp=datetime.datetime.utcfromtimestamp(0),
            ), update_result.read(mock_file))

    def test_writes_success_result_accurately(self):
        mock_file = io.StringIO()
        update_result.write(
            update_result.Result(
                success=True,
                error='',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), mock_file)
        self.assertEqual(('{"success": true, "error": "", '
                          '"timestamp": "2021-02-10T085735Z"}'),
                         mock_file.getvalue())

    def test_writes_error_result_accurately(self):
        mock_file = io.StringIO()
        update_result.write(
            update_result.Result(
                success=False,
                error='dummy update error',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), mock_file)
        self.assertEqual(('{"success": false, "error": "dummy update error", '
                          '"timestamp": "2021-02-10T085735Z"}'),
                         mock_file.getvalue())
