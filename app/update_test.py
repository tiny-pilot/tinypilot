import unittest
from unittest import mock

import update
import update_result


class UpdateTest(unittest.TestCase):

    @mock.patch.object(update.subprocess, 'check_output')
    @mock.patch.object(update.update_result_reader, 'read')
    def test_returns_not_running_when_there_is_no_process_nor_result_file(
            self, mock_read_update_result, mock_check_output):
        mock_check_output.return_value = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 224928  8612 ?        Ss   Apr03   0:01 /sbin/dummy-a
root        51  0.0  0.0 103152 21264 ?        Ss   Apr03   0:00 /lib/dummy-b
""".lstrip().encode('utf-8')
        mock_read_update_result.return_value = None

        status_actual, error_actual = update.get_current_state()
        self.assertEqual(update.Status.NOT_RUNNING, status_actual)
        self.assertIsNone(error_actual)

    @mock.patch.object(update.subprocess, 'check_output')
    @mock.patch.object(update.update_result_reader, 'read')
    def test_returns_running_when_update_process_is_running(
            self, mock_read_update_result, mock_check_output):
        mock_check_output.return_value = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 224928  8612 ?        Ss   Apr03   0:01 /sbin/dummy-a
root        51  0.0  0.0 103152 21264 ?        Ss   Apr03   0:00 /opt/tinypilot-privileged/update
""".lstrip().encode('utf-8')
        mock_read_update_result.return_value = None

        status_actual, error_actual = update.get_current_state()
        self.assertEqual(update.Status.IN_PROGRESS, status_actual)
        self.assertIsNone(error_actual)

    @mock.patch.object(update.subprocess, 'check_output')
    @mock.patch.object(update.update_result_reader, 'read')
    def test_ignores_update_result_if_update_is_running(self,
                                                        mock_read_update_result,
                                                        mock_check_output):
        """If update is running, last update result does not matter."""
        mock_check_output.return_value = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 224928  8612 ?        Ss   Apr03   0:01 /sbin/dummy-a
root        51  0.0  0.0 103152 21264 ?        Ss   Apr03   0:00 /opt/tinypilot-privileged/update
""".lstrip().encode('utf-8')
        # get_current_state should ignore this result because an update process
        # is currently running, which takes priority over the previous result.
        mock_read_update_result.return_value = update_result.Result(
            success=True, error=None, timestamp='2021-02-10T085735Z')

        status_actual, error_actual = update.get_current_state()
        self.assertEqual(update.Status.IN_PROGRESS, status_actual)
        self.assertIsNone(error_actual)

    @mock.patch.object(update.subprocess, 'check_output')
    @mock.patch.object(update.update_result_reader, 'read')
    def test_returns_success_when_no_process_is_running_and_last_run_was_ok(
            self, mock_read_update_result, mock_check_output):
        mock_check_output.return_value = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 224928  8612 ?        Ss   Apr03   0:01 /sbin/dummy-a
root        51  0.0  0.0 103152 21264 ?        Ss   Apr03   0:00 /lib/dummy-b
""".lstrip().encode('utf-8')
        mock_read_update_result.return_value = update_result.Result(
            success=True, error=None, timestamp='2021-02-10T085735Z')

        status_actual, error_actual = update.get_current_state()
        self.assertEqual(update.Status.DONE, status_actual)
        self.assertIsNone(error_actual)

    @mock.patch.object(update.subprocess, 'check_output')
    @mock.patch.object(update.update_result_reader, 'read')
    def test_returns_error_when_no_process_is_running_and_last_run_had_error(
            self, mock_read_update_result, mock_check_output):
        mock_check_output.return_value = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 224928  8612 ?        Ss   Apr03   0:01 /sbin/dummy-a
root        51  0.0  0.0 103152 21264 ?        Ss   Apr03   0:00 /lib/dummy-b
""".lstrip().encode('utf-8')
        mock_read_update_result.return_value = update_result.Result(
            success=False,
            error='dummy update error',
            timestamp='2021-02-10T085735Z')

        status_actual, error_actual = update.get_current_state()
        self.assertEqual(update.Status.DONE, status_actual)
        self.assertEqual('dummy update error', error_actual)
