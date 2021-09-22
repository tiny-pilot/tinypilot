import os
import tempfile
import unittest
from unittest import mock

import secret_key


class SecretKeyTest(unittest.TestCase):

    def assertSecretKeyValue(self, value):  # pylint: disable=invalid-name
        self.assertIs(bytes, type(value))
        self.assertEqual(32, len(value))

    def assertSecretKeyFile(self, value):  # pylint: disable=invalid-name
        self.assertTrue(os.path.exists(secret_key.SECRET_KEY_FILE))
        with open(secret_key.SECRET_KEY_FILE, 'rb') as f:  # pylint: disable=invalid-name
            self.assertEqual(value, f.read())

    def test_read_when_file_exists(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_secret_key_file = temp_file.name
            temp_file.write(b'insecure')
            temp_file.flush()

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # Returns exactly what's in the file.
                self.assertEqual(b'insecure', secret_key.read())

    def test_read_when_file_does_not_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_secret_key_file = os.path.join(temp_dir,
                                                secret_key.SECRET_KEY_FILE)
            self.assertFalse(os.path.exists(mock_secret_key_file))

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # Fails with an IOError.
                with self.assertRaises(IOError):
                    secret_key.read()

    def test_create_when_file_exists(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_secret_key_file = temp_file.name
            temp_file.write(b'insecure')
            temp_file.flush()

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # The file is overwritten with a new secret key.
                secret_key_value = secret_key.create()
                self.assertNotEqual(b'insecure', secret_key_value)
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)

    def test_create_when_file_does_not_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_secret_key_file = os.path.join(temp_dir,
                                                secret_key.SECRET_KEY_FILE)
            self.assertFalse(os.path.exists(mock_secret_key_file))

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # The file is created and a new secret key is written.
                secret_key_value = secret_key.create()
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)

    def test_get_when_file_exists(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_secret_key_file = temp_file.name
            temp_file.write(b'insecure')
            temp_file.flush()

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # Returns exactly what's in the file.
                secret_key_value = secret_key.get()
                self.assertEqual(b'insecure', secret_key_value)
                self.assertSecretKeyFile(secret_key_value)

    def test_get_when_an_invalid_secret_key_exists(self):
        with tempfile.NamedTemporaryFile() as temp_file:
            mock_secret_key_file = temp_file.name
            temp_file.write(b'')
            temp_file.flush()

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # The file is overwritten with a new secret key.
                secret_key_value = secret_key.get()
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)

    def test_get_when_file_does_not_exist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_secret_key_file = os.path.join(temp_dir,
                                                secret_key.SECRET_KEY_FILE)
            self.assertFalse(os.path.exists(mock_secret_key_file))

            with mock.patch.object(secret_key, 'SECRET_KEY_FILE',
                                   mock_secret_key_file):
                # The file is created and a new secret key is written.
                secret_key_value = secret_key.get()
                self.assertSecretKeyValue(secret_key_value)
                self.assertSecretKeyFile(secret_key_value)
