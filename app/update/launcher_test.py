import unittest
from unittest import mock

import update.status as update_status
from update import launcher

# pylint incorrectly complains that these methods could be free functions, but
# they need to be part of unittest.TestCase.
# pylint: disable=no-self-use


class LauncherTest(unittest.TestCase):

    @mock.patch.object(launcher.subprocess, 'Popen')
    @mock.patch.object(launcher.update.result_store, 'clear')
    @mock.patch.object(launcher.update.status, 'get')
    def test_launches_update_when_no_update_is_running(self, mock_status_get,
                                                       mock_clear, mock_popen):
        mock_status_get.return_value = (update_status.Status.NOT_RUNNING, '')

        launcher.start_async()

        mock_clear.assert_called()
        mock_popen.assert_called_once_with(
            ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))

    @mock.patch.object(launcher.subprocess, 'Popen')
    @mock.patch.object(launcher.update.result_store, 'clear')
    @mock.patch.object(launcher.update.status, 'get')
    def test_launches_update_when_previous_update_succeeded(
            self, mock_status_get, mock_clear, mock_popen):
        mock_status_get.return_value = (update_status.Status.DONE, '')

        launcher.start_async()

        mock_clear.assert_called()
        mock_popen.assert_called_once_with(
            ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))

    @mock.patch.object(launcher.subprocess, 'Popen')
    @mock.patch.object(launcher.update.result_store, 'clear')
    @mock.patch.object(launcher.update.status, 'get')
    def test_launches_update_when_previous_update_failed(
            self, mock_status_get, mock_clear, mock_popen):
        mock_status_get.return_value = (update_status.Status.DONE,
                                        'dummy updater failure message')

        launcher.start_async()

        mock_clear.assert_called_once()
        mock_popen.assert_called_once_with(
            ('sudo', '/usr/sbin/service', 'tinypilot-updater', 'start'))

    @mock.patch.object(launcher.subprocess, 'Popen')
    @mock.patch.object(launcher.update.result_store, 'clear')
    @mock.patch.object(launcher.update.status, 'get')
    def test_does_not_launch_if_update_is_already_running(
            self, mock_status_get, mock_clear, mock_popen):
        mock_status_get.return_value = (update_status.Status.IN_PROGRESS, '')

        with self.assertRaises(launcher.AlreadyInProgressError):
            launcher.start_async()

        mock_clear.assert_not_called()
        mock_popen.assert_not_called()
