import datetime
import io
import unittest

import update_result


class UpdateResultTest(unittest.TestCase):

    def test_reads_correct_values_for_successful_result(self):
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
                                     tzinfo=datetime.timezone.utc),
                                 version_at_end='1.4.2'),
            update_result.read(
                io.StringIO("""
{
  "success": true,
  "error": "",
  "timestamp": "2021-02-10T085735Z",
  "versionAtEnd": "1.4.2"
}
""")))

    def test_reads_correct_values_for_failed_result(self):
        self.assertEqual(
            update_result.Result(success=False,
                                 error='dummy update error',
                                 timestamp=datetime.datetime(
                                     2021,
                                     2,
                                     10,
                                     8,
                                     57,
                                     35,
                                     tzinfo=datetime.timezone.utc),
                                 version_at_end=''),
            update_result.read(
                io.StringIO("""
{
  "success": false,
  "error": "dummy update error",
  "timestamp": "2021-02-10T085735Z",
  "versionAtEnd": ""
}
""")))

    def test_reads_correct_values_for_legacy_result(self):
        """Make sure we can read legacy results that lack versionAtEnd field."""
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
                                     tzinfo=datetime.timezone.utc),
                                 version_at_end=''),
            update_result.read(
                io.StringIO("""
{
  "success": true,
  "error": "",
  "timestamp": "2021-02-10T085735Z"
}
""")))

    def test_reads_default_values_for_empty_dict(self):
        self.assertEqual(
            update_result.Result(
                success=False,
                error='',
                timestamp=datetime.datetime.utcfromtimestamp(0),
                version_at_end='',
            ), update_result.read(io.StringIO('{}')))

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
                version_at_end='1.4.2',
            ), mock_file)
        self.assertEqual(('{"success": true, "error": "", '
                          '"timestamp": "2021-02-10T085735Z", '
                          '"versionAtEnd": "1.4.2"}'), mock_file.getvalue())

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
                version_at_end='',
            ), mock_file)
        self.assertEqual(
            ('{"success": false, "error": "dummy update error", '
             '"timestamp": "2021-02-10T085735Z", "versionAtEnd": ""}'),
            mock_file.getvalue())
