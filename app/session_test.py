import tempfile
import unittest
from unittest import mock

import auth
import db.store
import db.users
import session
import video_service


def do_nothing():
    pass


class CheckAuthTest(unittest.TestCase):

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_grants_full_access_if_auth_requirement_is_off(
            self, mock_get_db, mock_username, mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            mock_username.return_value = None
            mock_credentials.return_value = None

            # The session is valid and satisfies all possible roles.
            self.assertTrue(session.is_auth_valid())
            self.assertTrue(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_grants_access_for_authenticated_admin(self, mock_get_db,
                                                   mock_username,
                                                   mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)
            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)
            admin = auth.get_account('admin')

            mock_username.return_value = 'admin'
            mock_credentials.return_value = admin.credentials_last_changed

            # The session is valid and satisfies all possible roles.
            self.assertTrue(session.is_auth_valid())
            self.assertTrue(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_denies_access_for_anonymous_visitor_if_auth_requirement_is_on(
            self, mock_get_db, mock_username, mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)
            mock_username.return_value = None
            mock_credentials.return_value = None

            # Auth requirement is off, so anonymous user is ok.
            self.assertTrue(session.is_auth_valid())
            self.assertTrue(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

            # Registering a user turns on the auth requirement.
            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)

            # Now, the anonymous user is blocked.
            self.assertFalse(session.is_auth_valid())
            self.assertFalse(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_denies_access_if_password_had_changed(self, mock_get_db,
                                                   mock_username,
                                                   mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)
            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)
            admin = auth.get_account('admin')

            # Initially, the user has access.
            mock_username.return_value = 'admin'
            mock_credentials.return_value = admin.credentials_last_changed
            self.assertTrue(session.is_auth_valid())
            self.assertTrue(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

            # After they change their credentials, their session expires.
            auth.change_password('admin', '12345')
            self.assertFalse(session.is_auth_valid())
            self.assertFalse(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_denies_access_if_session_corrupt(self, mock_get_db, mock_username,
                                              mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)
            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)
            admin = auth.get_account('admin')

            # `username` not set.
            mock_username.return_value = None
            mock_credentials.return_value = admin.credentials_last_changed
            self.assertFalse(session.is_auth_valid())
            self.assertFalse(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

            # `credentials_last_changed` not set.
            mock_username.return_value = 'admin'
            mock_credentials.return_value = None
            self.assertFalse(session.is_auth_valid())
            self.assertFalse(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(session, '_get_credentials_last_changed')
    @mock.patch.object(session, 'get_username')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_denies_access_if_user_is_deleted(self, mock_get_db, mock_username,
                                              mock_credentials):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)
            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)
            auth.register('second-admin', 'p4ssw0rd', auth.Role.ADMIN)
            admin = auth.get_account('admin')

            # Initially, the user has access.
            mock_username.return_value = 'admin'
            mock_credentials.return_value = admin.credentials_last_changed
            self.assertTrue(session.is_auth_valid())
            self.assertTrue(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))

            # Then, after deleting the account, the session expires.
            auth.delete_account('admin')
            self.assertFalse(session.is_auth_valid())
            self.assertFalse(
                session.is_auth_valid(satisfies_role=auth.Role.ADMIN))
