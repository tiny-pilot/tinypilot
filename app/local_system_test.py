import subprocess
import unittest
from unittest import mock

import local_system


class ExecShutdownTest(unittest.TestCase):

    def setUp(self):
        # Run all unit tests with debug mode disabled.
        is_debug_patch = mock.patch.object(local_system,
                                           '_is_debug',
                                           return_value=False)
        self.addCleanup(is_debug_patch.stop)
        is_debug_patch.start()

    @mock.patch.object(subprocess, 'run')
    def test_shutdown_runs_poweroff_command(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(args=[],
                                                            returncode=0,
                                                            stdout='',
                                                            stderr='')
        self.assertTrue(local_system.shutdown())
        mock_run.assert_called_once()
        self.assertIn('--poweroff', mock_run.call_args[0][0])

    @mock.patch.object(subprocess, 'run')
    def test_restart_runs_reboot_command(self, mock_run):
        mock_run.return_value = subprocess.CompletedProcess(args=[],
                                                            returncode=0,
                                                            stdout='',
                                                            stderr='')
        self.assertTrue(local_system.restart())
        mock_run.assert_called_once()
        self.assertIn('--reboot', mock_run.call_args[0][0])


class DebugModeTest(unittest.TestCase):

    @mock.patch.object(subprocess, 'run')
    def test_shutdown_does_not_run_command_in_debug_mode(self, mock_run):
        with mock.patch.object(local_system, '_is_debug', return_value=True):
            self.assertTrue(local_system.shutdown())
        mock_run.assert_not_called()

    @mock.patch.object(subprocess, 'run')
    def test_restart_does_not_run_command_in_debug_mode(self, mock_run):
        with mock.patch.object(local_system, '_is_debug', return_value=True):
            self.assertTrue(local_system.restart())
        mock_run.assert_not_called()
