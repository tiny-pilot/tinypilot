import tempfile
import unittest
from unittest import mock

import auth
import db.store
import db.users
import utc
import video_service


def do_nothing():
    pass


class RoleTest(unittest.TestCase):

    def test_role_stringifies_to_defined_values(self):
        # This test is to help us remember that we can’t just change the role’s
        # names in the code, because we serialize the names (e.g. in the DB),
        # so they must be somewhat stable (or we have to properly migrate).
        self.assertEqual('ADMIN', auth.Role.ADMIN.name)
        self.assertEqual('OPERATOR', auth.Role.OPERATOR.name)

    def test_role_values_evaluate_to_true(self):
        # This is a critical prerequisite for modelling auth checks so that the
        # presence of a role corresponds to authenticated/authorized, and the
        # absence of a role (`None`) means unauthenticated/unauthorized.
        self.assertTrue(auth.Role.ADMIN)
        self.assertTrue(auth.Role.OPERATOR)


class AuthTest(unittest.TestCase):

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_can_authenticate_with_valid_credentials(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            self.assertTrue(auth.can_authenticate('pilot', 'p4ssw0rd'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_register_duplicate_users(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', '12345', auth.Role.ADMIN)
            with self.assertRaises(db.users.UserAlreadyExistsError):
                auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_fails_if_first_user_is_not_admin(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            with self.assertRaises(auth.OneAdminRequiredError):
                auth.register('pilot', '12345', auth.Role.OPERATOR)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_authenticate_with_wrong_password(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            self.assertFalse(auth.can_authenticate('pilot', '12345'))

    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_authenticate_when_no_user_is_registered(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            self.assertFalse(auth.can_authenticate('pilot', '12345'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_authenticate_with_unknown_user(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            self.assertFalse(auth.can_authenticate('someone-else', 'p4ssw0rd'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_authenticate_after_account_deletion(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            # Create dummy admin user to satisfy the “one admin required”
            # constraint.
            auth.register('dummy-admin', '12345', auth.Role.ADMIN)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.delete_account('pilot')
            self.assertFalse(auth.can_authenticate('pilot', 'p4ssw0rd'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_delete_last_remaining_admin_while_other_users_exist(
            self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)

            # Creating an additional OPERATOR user doesn’t allow deleting the
            # ADMIN user.
            auth.register('operator', 'p4ssw0rd', auth.Role.OPERATOR)
            with self.assertRaises(auth.OneAdminRequiredError):
                auth.delete_account('admin')

            # Only creating another ADMIN user lets us delete the first one.
            auth.register('second-admin', 'p4ssw0rd', auth.Role.ADMIN)
            auth.delete_account('admin')

            # Now, the other ADMIN user is “locked” because it's the last ADMIN
            # on the system.
            with self.assertRaises(auth.OneAdminRequiredError):
                auth.delete_account('second-admin')

            # Deleting the OPERATOR user doesn’t produce any error, though.
            auth.delete_account('operator')

            # Eventually, the last remaining ADMIN user is safe to delete
            # because there are no other users on the system.
            auth.delete_account('second-admin')

    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_delete_unknown_user(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            with self.assertRaises(db.users.UserDoesNotExistError):
                auth.delete_account('pilot')

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_authenticate_after_all_accounts_deleted(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.register('new-pilot', 'pa55word', auth.Role.ADMIN)
            auth.delete_all_accounts()
            self.assertEqual([], auth.get_all_accounts())
            self.assertFalse(auth.can_authenticate('pilot', 'p4ssw0rd'))
            self.assertFalse(auth.can_authenticate('new-pilot', 'pa55word'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_system_supports_multiple_user_accounts(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.register('new-pilot', 'pa55word', auth.Role.ADMIN)
            self.assertTrue(auth.can_authenticate('pilot', 'p4ssw0rd'))
            self.assertTrue(auth.can_authenticate('new-pilot', 'pa55word'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_authentication_required_when_users_exist(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            self.assertFalse(auth.is_authentication_required())

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            self.assertTrue(auth.is_authentication_required())
            auth.register('another-pilot', '12345', auth.Role.ADMIN)
            self.assertTrue(auth.is_authentication_required())

            auth.delete_all_accounts()
            self.assertFalse(auth.is_authentication_required())

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_can_authenticate_after_changing_password(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.change_password('pilot', 'pa55word')
            self.assertFalse(auth.can_authenticate('pilot', 'p4ssw0rd'))
            self.assertTrue(auth.can_authenticate('pilot', 'pa55word'))

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_change_credentials_of_unknown_user(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            # Create dummy admin user to satisfy the “one admin required”
            # constraint.
            auth.register('dummy-admin', '12345', auth.Role.ADMIN)

            with self.assertRaises(db.users.UserDoesNotExistError):
                auth.change_password('pilot', 'p4ssw0rd')

            with self.assertRaises(db.users.UserDoesNotExistError):
                auth.change_role('pilot', auth.Role.OPERATOR)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_cannot_change_role_of_last_remaining_admin(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('admin', 'p4ssw0rd', auth.Role.ADMIN)
            with self.assertRaises(auth.OneAdminRequiredError):
                auth.change_role('admin', auth.Role.OPERATOR)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_get_account(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            self.assertEqual([], auth.get_all_accounts())
            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.register('another-pilot', 'pa55word', auth.Role.OPERATOR)

            pilot = auth.get_account('pilot')
            self.assertEqual('pilot', pilot.username)
            self.assertEqual(auth.Role.ADMIN, pilot.role)

            another_pilot = auth.get_account('another-pilot')
            self.assertEqual('another-pilot', another_pilot.username)
            self.assertEqual(auth.Role.OPERATOR, another_pilot.role)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_get_all_accounts(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            self.assertEqual([], auth.get_all_accounts())
            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            auth.register('another-pilot', 'pa55word', auth.Role.ADMIN)
            auth.register('yet-another-pilot', 'pa55word', auth.Role.OPERATOR)

            users = auth.get_all_accounts()

            self.assertEqual('pilot', users[0].username)
            self.assertEqual(auth.Role.ADMIN, users[0].role)

            self.assertEqual('another-pilot', users[1].username)
            self.assertEqual(auth.Role.ADMIN, users[1].role)

            self.assertEqual('yet-another-pilot', users[2].username)
            self.assertEqual(auth.Role.OPERATOR, users[2].role)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_sets_credentials_timestamp_on_registration(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            before = utc.now()
            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            after = utc.now()
            self.assertTrue(before <= auth.get_account(
                'pilot').credentials_last_changed <= after)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_updates_credentials_timestamp_when_changing_password(
            self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            initial_timestamp = auth.get_account(
                'pilot').credentials_last_changed

            before = utc.now()
            auth.change_password('pilot', 'pa55word')
            after = utc.now()

            self.assertNotEqual(
                initial_timestamp,
                auth.get_account('pilot').credentials_last_changed)
            self.assertTrue(before <= auth.get_account(
                'pilot').credentials_last_changed <= after)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_updates_credentials_timestamp_when_changing_role(
            self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            # Create dummy admin user to satisfy the “one admin required”
            # constraint.
            auth.register('dummy-admin', '12345', auth.Role.ADMIN)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            initial_timestamp = auth.get_account(
                'pilot').credentials_last_changed

            before = utc.now()
            auth.change_role('pilot', auth.Role.OPERATOR)
            after = utc.now()

            self.assertNotEqual(
                initial_timestamp,
                auth.get_account('pilot').credentials_last_changed)
            self.assertTrue(before <= auth.get_account(
                'pilot').credentials_last_changed <= after)

    @mock.patch.object(video_service, 'restart', do_nothing)
    @mock.patch.object(db.users.db_connection, 'get')
    def test_updates_role_when_changing_role(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            # Create dummy admin user to satisfy the “one admin required”
            # constraint.
            auth.register('dummy-admin', '12345', auth.Role.ADMIN)

            auth.register('pilot', 'p4ssw0rd', auth.Role.ADMIN)
            self.assertEqual(auth.Role.ADMIN, auth.get_account('pilot').role)

            auth.change_role('pilot', auth.Role.OPERATOR)
            self.assertEqual(auth.Role.OPERATOR, auth.get_account('pilot').role)

    @mock.patch.object(db.users.db_connection, 'get')
    def test_raises_if_user_does_not_exist(self, mock_get_db):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            with self.assertRaises(db.users.UserDoesNotExistError):
                auth.get_account('pilot')

    @mock.patch.object(video_service, 'restart')
    @mock.patch.object(db.users.db_connection, 'get')
    def test_restarts_video_service_after_credentials_change(
            self, mock_get_db, mock_video_service_restart):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_get_db.return_value = db.store.create_or_open(temp_file.name)

            # Create dummy admin user to satisfy the “one admin required”
            # constraint.
            auth.register('dummy-admin', '12345', auth.Role.ADMIN)
            self.assertEqual(mock_video_service_restart.call_count, 1)

            auth.register('pilot', 'p4assw0rd', auth.Role.ADMIN)
            self.assertEqual(mock_video_service_restart.call_count, 2)

            auth.change_password('pilot', 'pa55word')
            self.assertEqual(mock_video_service_restart.call_count, 3)

            auth.change_role('pilot', auth.Role.OPERATOR)
            self.assertEqual(mock_video_service_restart.call_count, 4)

            auth.delete_account('pilot')
            self.assertEqual(mock_video_service_restart.call_count, 5)

            auth.delete_all_accounts()
            self.assertEqual(mock_video_service_restart.call_count, 6)
