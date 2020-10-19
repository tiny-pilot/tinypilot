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
                'vwheel': 0,
                'hwheel': 0,
            }))

    def test_parses_valid_mouse_event_with_int_position(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=1, relative_x=0.0, relative_y=0.75),
            mouse_event.parse_mouse_event({
                'buttons': 1,
                'relativeX': 0,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            }))

    def test_parses_valid_mouse_event_with_all_buttons_pressed(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=31, relative_x=0.5, relative_y=0.75),
            mouse_event.parse_mouse_event({
                'buttons': 31,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            }))

    def test_rejects_negative_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': -1,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_too_high_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': 32,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_non_numeric_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': 'a',
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_negative_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': -0.001,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_negative_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': -0.001,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_too_high_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 1.001,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_too_high_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 1.001,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_non_float_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 'a',
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_non_float_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 'b',
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_missing_buttons_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'relativeX': 0,
                'relativeY': 0,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_missing_relative_x_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeY': 0,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_missing_relative_y_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'vwheel': 0,
                'hwheel': 0,
            })

    def test_rejects_missing_v_wheel_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'hwheel': 0,
            })

    def test_rejects_missing_h_wheel_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'vwheel': 0,
            })

    def test_rejects_non_int_v_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 'a',
                'hwheel': 0,
            })

    def test_rejects_non_int_h_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'vwheel': 0,
                'hwheel': 'a',
            })
