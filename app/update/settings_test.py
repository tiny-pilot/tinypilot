import os.path
import tempfile
import unittest
from unittest import mock

import update.settings


class UpdateSettingsTest(unittest.TestCase):

    def setUp(self):
        # Mock out the path to the settings.yml file so that it points to a file
        # path that the test controls.

        # Ignore pylint because we perform a tear down and assert the temporary
        # files are gone.
        # pylint: disable=consider-using-with
        self.mock_settings_dir = tempfile.TemporaryDirectory()
        self.settings_file_path = os.path.join(self.mock_settings_dir.name,
                                               'settings.yml')

        path_patch = mock.patch.object(update.settings, '_SETTINGS_FILE_PATH',
                                       self.settings_file_path)
        self.addCleanup(path_patch.stop)
        path_patch.start()

    def tearDown(self):
        self.mock_settings_dir.cleanup()

    def make_mock_settings_file(self, contents):
        with open(self.settings_file_path, 'w', encoding='utf-8') as mock_file:
            mock_file.write(contents)

    def read_mock_settings_file(self):
        with open(self.settings_file_path, encoding='utf-8') as mock_file:
            return mock_file.read()

    def test_returns_empty_settings_if_no_settings_file_exists(self):
        self.assertEqual({}, update.settings.load().as_dict())

    def test_populates_empty_file_with_blank_settings(self):
        self.make_mock_settings_file('')

        settings = update.settings.load()
        update.settings.save(settings)

        self.assertEqual('', self.read_mock_settings_file())

    def test_populates_empty_file_with_branch_name(self):
        self.make_mock_settings_file('')

        settings = update.settings.load()
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
""".lstrip(), self.read_mock_settings_file())

    def test_overwrites_existing_branch_name(self):
        self.make_mock_settings_file("""
tinypilot_repo_branch: branch-name-to-overwrite
""".lstrip())

        settings = update.settings.load()
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
""".lstrip(), self.read_mock_settings_file())

    def test_leaves_unrecognized_settings_intact(self):
        self.make_mock_settings_file("""
tinypilot_repo_branch: branch-name-to-overwrite
unrecognized_setting: dummyvalue
""".lstrip())

        settings = update.settings.load()
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
unrecognized_setting: dummyvalue
""".lstrip(), self.read_mock_settings_file())
