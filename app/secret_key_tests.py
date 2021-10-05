import os
import stat
import tempfile
import unittest
from unittest import mock

import secret_key


class SecretKeyTest(unittest.TestCase):

    # Intentionally violating style conventions so that we can parallel the
    # self.assertEqual method.
    def assertSecretKeyValue(self, value):  # pylint: disable=invalid-name
        self.assertIs(bytes, type(value))
        self.assertEqual(32, len(value))

    def assertSecretKeyFile(self, value):  # pylint: disable=invalid-name
        self.assertTrue(os.path.exists(secret_key._SECRET_KEY_FILE))  # pylint: disable=protected-access
        file_perms = stat.S_IMODE(os.stat(secret_key._SECRET_KEY_FILE).st_mode)  # pylint: disable=protected-access
        self.assertEqual(0o600, file_perms)
        with open(secret_key._SECRET_KEY_FILE, 'rb') as key_file:  # pylint: disable=protected-access
            self.assertEqual(value, key_file.read())

    def test_get_or_create_will_get_when_valid_file_exists(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_secret_key_file = temp_file.name
            temp_file.write(b'00000000000000000000000000000000')
            temp_file.flush()

            with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                   mock_secret_key_file):
                secret_key_value = secret_key.get_or_create()
                self.assertEqual(b'00000000000000000000000000000000',
                                 secret_key_value)
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)

    def test_get_or_create_will_overwrite_when_invalid_file_exists(self):

        with self.subTest('Wrong file permissions'):
            with tempfile.NamedTemporaryFile() as temp_file:
                mock_secret_key_file = temp_file.name
                temp_file.write(b'00000000000000000000000000000000')
                temp_file.flush()
                os.chmod(mock_secret_key_file, 0o700)

                with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                       mock_secret_key_file):
                    secret_key_value = secret_key.get_or_create()
                    self.assertNotEqual(b'00000000000000000000000000000000',
                                        secret_key_value)
                    self.assertSecretKeyValue(secret_key_value)
                    self.assertSecretKeyFile(secret_key_value)

        with self.subTest('Not a string of 32 bytes'):
            with tempfile.NamedTemporaryFile() as temp_file:
                mock_secret_key_file = temp_file.name
                temp_file.write(b'invalid')
                temp_file.flush()

                with mock.patch.object(secret_key, '_SECRET_KEY_FILE',
                                       mock_secret_key_file):
                    secret_key_value = secret_key.get_or_create()
                    self.assertNotEqual(b'invalid', secret_key_value)
                    self.assertSecretKeyValue(secret_key_value)
                    self.assertSecretKeyFile(secret_key_value)

    def test_get_or_create_will_create_when_file_does_not_exist(self):
        with tempfile.TemporaryDirectory() as mock_secret_key_dir:

            with mock.patch.object(secret_key, '_SECRET_KEY_DIR',
                                   mock_secret_key_dir):
                secret_key_value = secret_key.get_or_create()
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)
