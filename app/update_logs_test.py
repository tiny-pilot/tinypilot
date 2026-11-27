import unittest
from unittest import mock

import update_logs


class UpdateLogsTest(unittest.TestCase):

    def test_get_new_logs_with_more_next_logs(self):
        self.assertEqual(
            '56789',
            update_logs.get_new_logs(prev_logs='01234', next_logs='0123456789'))

    def test_get_new_logs_with_more_prev_logs(self):
        self.assertEqual(
            '',
            update_logs.get_new_logs(prev_logs='0123456789', next_logs='01234'))

    def test_get_new_logs_with_no_common_logs(self):
        self.assertEqual(
            '56789',
            update_logs.get_new_logs(prev_logs='01234', next_logs='56789'))

    def test_get_new_logs_with_no_prev_logs(self):
        self.assertEqual(
            '0123456789',
            update_logs.get_new_logs(prev_logs='', next_logs='0123456789'))

    def test_get_new_logs_with_no_next_logs(self):
        self.assertEqual(
            '', update_logs.get_new_logs(prev_logs='01234', next_logs=''))

    @mock.patch('update_logs.session.is_auth_valid', return_value=False)
    def test_on_connect_rejects_unauthenticated(self, mock_is_auth_valid):
        namespace = update_logs.Namespace('/updateLogs')
        self.assertFalse(namespace.on_connect())
        self.assertEqual(0, namespace.client_count)
        mock_is_auth_valid.assert_called_once_with(
            satisfies_role=update_logs.auth.Role.ADMIN)

    @mock.patch('update_logs.session.is_auth_valid', return_value=True)
    def test_on_connect_allows_admin(self, mock_is_auth_valid):
        namespace = update_logs.Namespace('/updateLogs')
        namespace.on_connect()
        self.assertEqual(1, namespace.client_count)
        mock_is_auth_valid.assert_called_once_with(
            satisfies_role=update_logs.auth.Role.ADMIN)

    @mock.patch('update_logs.flask_socketio.disconnect')
    @mock.patch('update_logs.session.is_auth_valid', return_value=False)
    def test_on_start_rejects_unauthenticated(self, mock_is_auth_valid,
                                              mock_disconnect):
        namespace = update_logs.Namespace('/updateLogs')
        namespace.on_start()
        self.assertFalse(namespace.is_streaming)
        mock_disconnect.assert_called_once_with()
        mock_is_auth_valid.assert_called_once_with(
            satisfies_role=update_logs.auth.Role.ADMIN)
