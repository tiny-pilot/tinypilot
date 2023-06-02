import io
import unittest

import render_template


class RenderTemplateTest(unittest.TestCase):

    def test_renders_with_no_overrides(self):
        rendered_actual = render_template.render(
            default_settings={
                'tinypilot_keyboard_interface': '/dev/hidg0',
                'tinypilot_mouse_interface': '/dev/hidg1',
            },
            user_overrides_file=io.StringIO(''),
            template_file=io.StringIO("""
KEYBOARD_PATH = '{{ tinypilot_keyboard_interface }}'
MOUSE_PATH = '{{ tinypilot_mouse_interface }}'
"""))
        self.assertEqual(
            """
KEYBOARD_PATH = '/dev/hidg0'
MOUSE_PATH = '/dev/hidg1'
""".rstrip(), rendered_actual)

    def test_user_overrides_take_precedence_over_defaults(self):
        rendered_actual = render_template.render(
            default_settings={
                'tinypilot_keyboard_interface': '/dev/hidg0',
                'tinypilot_mouse_interface': '/dev/hidg1',
            },
            user_overrides_file=io.StringIO("""
tinypilot_keyboard_interface: '/dev/null'
            """),
            template_file=io.StringIO("""
KEYBOARD_PATH = '{{ tinypilot_keyboard_interface }}'
MOUSE_PATH = '{{ tinypilot_mouse_interface }}'
"""))
        self.assertEqual(
            """
KEYBOARD_PATH = '/dev/null'
MOUSE_PATH = '/dev/hidg1'
""".rstrip(), rendered_actual)
