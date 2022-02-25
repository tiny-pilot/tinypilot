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

    def test_chmod_sets_desired_permissions(self):
        file_path_1 = os.path.join(self.destination_dir.name, 'test1.txt')
        with atomic_file.create(file_path_1, chmod_mode=0o770) as file:
            file.write(bytes('hello world', 'utf-8'))

        permissions_1 = stat.S_IMODE(os.stat(file_path_1).st_mode)
        self.assertEqual(0o770, permissions_1)

        # Run the test a second time with different permissions, so that we can
        # rule out the case where the specified permissions would accidentally
        # happen to match the system default.
        file_path_2 = os.path.join(self.destination_dir.name, 'test2.txt')
        with atomic_file.create(file_path_2, chmod_mode=0o666) as file:
            file.write(bytes('hello world', 'utf-8'))

        permissions = stat.S_IMODE(os.stat(file_path_2).st_mode)
        self.assertEqual(0o666, permissions)

    def test_chmod_falls_back_to_system_default(self):
        file_path = os.path.join(self.destination_dir.name, 'test.txt')

        with atomic_file.create(file_path) as file:
            file.write(bytes('hello world', 'utf-8'))
        atomic_file_permissions = stat.S_IMODE(os.stat(file_path).st_mode)

        # Create a temporary dummy file, to find out what chmod value new files
        # are created with by default. Default file permissions depend on the
        # umask setting of the system/process.
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(bytes('', 'utf-8'))
            default_permissions = stat.S_IMODE(os.stat(tmp.name).st_mode)

        self.assertEqual(default_permissions, atomic_file_permissions)

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
