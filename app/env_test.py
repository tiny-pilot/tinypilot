import unittest

import env


class EnvTest(unittest.TestCase):

    def test_accepts_file_in_home_dir(self):
        file = env.abs_path_in_home_dir('file')
        self.assertEqual('/home/tinypilot/file', file)

    def test_accepts_folder_in_home_dir(self):
        folder = env.abs_path_in_home_dir('folder/')
        self.assertEqual('/home/tinypilot/folder', folder)

    def test_accepts_nested_path_within_home_dir(self):
        nested_path = env.abs_path_in_home_dir('nested/path')
        self.assertEqual('/home/tinypilot/nested/path', nested_path)

    def test_accepts_path_traversal_within_home_dir(self):
        nested_path = env.abs_path_in_home_dir('folder/../file')
        self.assertEqual('/home/tinypilot/file', nested_path)

    def test_rejects_input_with_leading_slash(self):
        with self.assertRaises(ValueError):
            env.abs_path_in_home_dir('/foo')

    def test_rejects_path_traversal_outside_home_dir(self):
        with self.assertRaises(ValueError):
            env.abs_path_in_home_dir('../foo')

        with self.assertRaises(ValueError):
            env.abs_path_in_home_dir('foo/../../bar')
