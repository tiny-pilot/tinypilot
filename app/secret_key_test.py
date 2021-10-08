import os
import stat
import tempfile
import unittest
from unittest import mock

import secret_key


class SecretKeyTest(unittest.TestCase):

    def test_get_or_create_will_get_when_valid_file_exists(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'0' * 32)
            mock_secret_key_file.flush()

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                secret_key_value = secret_key.get_or_create()
                self.assertEqual(b'0' * 32, secret_key_value)

    def test_get_or_create_will_raise_error_when_file_has_invalid_perms(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'0' * 32)
            mock_secret_key_file.flush()
            os.chmod(mock_secret_key_file.name, 0o700)

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                with self.assertRaises(secret_key.InvalidSecretKeyError):
                    secret_key.get_or_create()

    def test_get_or_create_will_raise_error_when_file_has_invalid_content(self):
        with tempfile.NamedTemporaryFile() as mock_secret_key_file:
            mock_secret_key_file.write(b'dummy key data with incorrect size')
            mock_secret_key_file.flush()

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file.name):
                with self.assertRaises(secret_key.InvalidSecretKeyError):
                    secret_key.get_or_create()

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
                self.assertIs(bytes, type(secret_key_value))
                self.assertEqual(32, len(secret_key_value))
