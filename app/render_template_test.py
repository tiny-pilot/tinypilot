import io
import unittest

import render_template


class RenderTemplateTest(unittest.TestCase):

    def test_renders_when_no_overrides_exist(self):
        mock_template_file = io.StringIO(
            'TinyPilot is listening on port {{ tinypilot_external_port }}.')

        mock_overrides_file = io.StringIO('')

        self.assertEqual(
            'TinyPilot is listening on port 123.',
            render_template.render({'tinypilot_external_port': 123},
                                   mock_overrides_file, mock_template_file))

    def test_overrides_replace_default_settings(self):
        mock_template_file = io.StringIO(
            'TinyPilot is listening on port {{ tinypilot_external_port }}.')

        mock_overrides_file = io.StringIO("""
---
tinypilot_external_port: 321
""")

        self.assertEqual(
            'TinyPilot is listening on port 321.',
            render_template.render({'tinypilot_external_port': 123},
                                   mock_overrides_file, mock_template_file))
