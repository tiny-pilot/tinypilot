import datetime
import io
import unittest

import update_result


class UpdateResultTest(unittest.TestCase):

    def test_reads_correct_values_for_successful_result(self):
        self.assertEqual(
            update_result.Result(
                error='',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ),
            update_result.read(
                io.StringIO("""
{
  "error": "",
  "timestamp": "2021-02-10T085735Z"
}
""")))

    def test_reads_correct_values_for_failed_result(self):
        self.assertEqual(
            update_result.Result(
                error='dummy update error',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ),
            update_result.read(
                io.StringIO("""
{
  "error": "dummy update error",
  "timestamp": "2021-02-10T085735Z"
}
""")))

    def test_reads_default_values_for_empty_dict(self):
        self.assertEqual(
            update_result.Result(
                error='',
                timestamp=datetime.datetime.utcfromtimestamp(0),
            ), update_result.read(io.StringIO('{}')))

    def test_writes_success_result_accurately(self):
        mock_file = io.StringIO()
        update_result.write(
            update_result.Result(
                error='',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), mock_file)
        self.assertEqual(('{"error": "", "timestamp": "2021-02-10T085735Z"}'),
                         mock_file.getvalue())

    def test_writes_error_result_accurately(self):
        mock_file = io.StringIO()
        update_result.write(
            update_result.Result(
                error='dummy update error',
                timestamp=datetime.datetime(2021,
                                            2,
                                            10,
                                            8,
                                            57,
                                            35,
                                            tzinfo=datetime.timezone.utc),
            ), mock_file)
        self.assertEqual(('{"error": "dummy update error", '
                          '"timestamp": "2021-02-10T085735Z"}'),
                         mock_file.getvalue())
