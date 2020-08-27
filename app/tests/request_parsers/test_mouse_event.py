import unittest

from request_parsers import mouse_event


class MouseEventTest(unittest.TestCase):

    def test_parses_valid_mouse_event(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=1, relative_x=0.5, relative_y=0.75),
            mouse_event.parse_mouse_event({
                'buttons': 1,
                'relativeX': 0.5,
                'relativeY': 0.75,
            }))

    def test_parses_valid_mouse_event_with_all_buttons_pressed(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=31, relative_x=0.5, relative_y=0.75),
            mouse_event.parse_mouse_event({
                'buttons': 31,
                'relativeX': 0.5,
                'relativeY': 0.75,
            }))

    def test_rejects_negative_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': -1,
                'relativeX': 0.5,
                'relativeY': 0.75,
            })

    def test_rejects_too_high_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': 32,
                'relativeX': 0.5,
                'relativeY': 0.75,
            })

    def test_rejects_negative_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': -0.001,
                'relativeY': 0.75,
            })

    def test_rejects_negative_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': -0.001,
            })

    def test_rejects_too_high_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 1.001,
                'relativeY': 0.75,
            })

    def test_rejects_too_high_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 1.001,
            })

    # TODO(mtlynch): Add tests for non-numeric values.
