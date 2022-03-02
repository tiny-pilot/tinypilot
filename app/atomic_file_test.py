import os
import stat
import tempfile
import unittest
from unittest import mock

import atomic_file


class CallerError(Exception):
    pass


class AtomicFileTest(unittest.TestCase):

    def setUp(self):
        self.destination_dir = tempfile.TemporaryDirectory()

        self.temp_dir = tempfile.TemporaryDirectory()
        intermediate_files_path_patch = mock.patch.object(
            atomic_file, '_TEMP_FOLDER', self.temp_dir.name)
        self.addCleanup(intermediate_files_path_patch.stop)
        intermediate_files_path_patch.start()

    def tearDown(self):
        self.destination_dir.cleanup()
        self.temp_dir.cleanup()

    # Ignore pylint because we want to have naming consistent with other
    # unittest.TestCase assert methods.
    # pylint: disable=invalid-name
    def assertFileContainsData(self, path, data_expected):
        self.assertTrue(os.path.exists(path))
        with open(path, 'rb') as file:
            data_actual = file.read()
            self.assertEqual(data_expected, data_actual)

    # Ignore pylint because we want to have naming consistent with other
    # unittest.TestCase assert methods.
    # pylint: disable=invalid-name
    def assertFolderIsEmpty(self, path):
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.isdir(path))
        self.assertEqual([], os.listdir(path))

    def test_persists_new_file_in_destination_folder(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')
        with atomic_file.create(file_path) as file:
            file.write(bytes('hello world', 'utf-8'))

        saved_path = os.path.join(self.destination_dir.name, 'test.txt')
        self.assertFileContainsData(saved_path, bytes('hello world', 'utf-8'))
        self.assertFolderIsEmpty(self.temp_dir.name)

    def test_chmod_uses_0600_as_default_mode(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')
        with atomic_file.create(file_path) as file:
            file.write(bytes('hello world', 'utf-8'))

        permissions = stat.S_IMODE(os.stat(file_path).st_mode)
        self.assertEqual(0o600, permissions)

    def test_chmod_sets_desired_permissions(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')
        with atomic_file.create(file_path, chmod_mode=0o770) as file:
            file.write(bytes('hello world', 'utf-8'))

        permissions = stat.S_IMODE(os.stat(file_path).st_mode)
        self.assertEqual(0o770, permissions)

    def test_cleans_up_temp_file_on_os_error(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')
        m = mock.mock_open()
        with mock.patch('atomic_file.open', m) as open_patch:
            open_patch.side_effect = mock.Mock(side_effect=OSError())
            with self.assertRaises(OSError):
                with atomic_file.create(file_path) as file:
                    file.write(bytes('hello world', 'utf-8'))

        # The temporary file should be gone and there also shouldn’t be a
        # partial file at the destination location.
        self.assertFolderIsEmpty(self.destination_dir.name)
        self.assertFolderIsEmpty(self.temp_dir.name)

    def test_cleans_up_temp_file_on_caller_error(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')
        try:
            with atomic_file.create(file_path) as file:
                # Caller begins writing into the file:
                file.write(bytes('hello world', 'utf-8'))
                # Then, the caller raises an error:
                raise CallerError()
        except CallerError:
            pass

        # The temporary file should be gone and there also shouldn’t be a
        # partial file at the destination location.
        self.assertFolderIsEmpty(self.destination_dir.name)
        self.assertFolderIsEmpty(self.temp_dir.name)
