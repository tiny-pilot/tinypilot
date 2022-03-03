import os
import stat
import tempfile
import unittest
from unittest import mock

import secret_key


class SecretKeyTest(unittest.TestCase):

    def assertIsValidKeyValue(self, secret_key_value):  # pylint: disable=invalid-name
        self.assertIs(bytes, type(secret_key_value))
        self.assertEqual(32, len(secret_key_value))

    def test_get_or_create_will_get_when_valid_file_exists(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'0' * 32)
            mock_secret_key_file.flush()

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                secret_key_value = secret_key.get_or_create()
                self.assertEqual(b'0' * 32, secret_key_value)

    def test_get_or_create_will_recreate_if_file_has_invalid_perms(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'0' * 32)
            mock_secret_key_file.flush()
            os.chmod(mock_secret_key_file.name, 0o700)

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                secret_key_value = secret_key.get_or_create()
                self.assertIsValidKeyValue(secret_key_value)
                self.assertNotEqual(b'0' * 32, secret_key_value)
                file_perms = stat.S_IMODE(
                    os.stat(mock_secret_key_file.name).st_mode)
                self.assertEqual(0o600, file_perms)

    def test_get_or_create_will_recreate_file_if_content_is_corrupt(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'invalid key')
            mock_secret_key_file.flush()

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                secret_key_value = secret_key.get_or_create()
                self.assertIsValidKeyValue(secret_key_value)
                self.assertNotEqual(b'invalid key', secret_key_value)

    def test_get_or_create_will_create_when_file_does_not_exist(self):
        with tempfile.TemporaryDirectory() as mock_secret_key_dir:
            mock_secret_key_file = os.path.join(mock_secret_key_dir,
                                                'secret-key-file')

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file):
                self.assertFalse(os.path.exists(mock_secret_key_file))
                secret_key_value = secret_key.get_or_create()
                self.assertTrue(os.path.exists(mock_secret_key_file))
                file_perms = stat.S_IMODE(os.stat(mock_secret_key_file).st_mode)
                self.assertEqual(0o600, file_perms)
                self.assertIsValidKeyValue(secret_key_value)

                # Verify that the file was actually persisted by retrieving it
                # again and then checking that the value is still the same.
                reread_secret_key_value = secret_key.get_or_create()
                self.assertEqual(secret_key_value, reread_secret_key_value)
