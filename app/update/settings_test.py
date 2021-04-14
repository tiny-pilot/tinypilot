import io
import unittest

import update.settings


class UpdateSettingsTest(unittest.TestCase):

    def test_populates_empty_file_blank_settings(self):
        mock_input_file = io.StringIO()
        mock_output_file = io.StringIO()

        settings = update.settings.load(mock_input_file)
        update.settings.save(settings, mock_output_file)

        self.assertEqual('', mock_output_file.getvalue())

    def test_populates_empty_file_with_branch_name(self):
        mock_input_file = io.StringIO()
        mock_output_file = io.StringIO()

        settings = update.settings.load(mock_input_file)
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings, mock_output_file)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
""".lstrip(), mock_output_file.getvalue())

    def test_overwrites_existing_branch_name(self):
        mock_input_file = io.StringIO("""
tinypilot_repo_branch: branch-name-to-overwrite
""".lstrip())
        mock_output_file = io.StringIO()

        settings = update.settings.load(mock_input_file)
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings, mock_output_file)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
""".lstrip(), mock_output_file.getvalue())

    def test_leaves_unrecognized_settings_intact(self):
        mock_input_file = io.StringIO("""
tinypilot_repo_branch: branch-name-to-overwrite
unrecognized_setting: dummyvalue
""".lstrip())
        mock_output_file = io.StringIO()

        settings = update.settings.load(mock_input_file)
        settings.tinypilot_repo_branch = 'dummy-branch-name'
        update.settings.save(settings, mock_output_file)

        self.assertMultiLineEqual(
            """
tinypilot_repo_branch: dummy-branch-name
unrecognized_setting: dummyvalue
""".lstrip(), mock_output_file.getvalue())
