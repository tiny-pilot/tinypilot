import unittest

from request_parsers import mouse_event


class MouseEventTest(unittest.TestCase):

    def test_parses_valid_mouse_event(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=1,
                                   relative_x=0.5,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=0),
            mouse_event.parse_mouse_event({
                'buttons': 1,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            }))

    def test_parses_valid_mouse_event_with_int_position(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=1,
                                   relative_x=0.0,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=0),
            mouse_event.parse_mouse_event({
                'buttons': 1,
                'relativeX': 0,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            }))

    def test_parses_valid_negative_vertical_scroll(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=0,
                                   relative_x=0.0,
                                   relative_y=0.75,
                                   vertical_wheel_delta=-1,
                                   horizontal_wheel_delta=0),
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'relativeY': 0.75,
                'verticalWheelDelta': -1,
                'horizontalWheelDelta': 0,
            }))

    def test_parses_valid_positive_vertical_scroll(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=0,
                                   relative_x=0.0,
                                   relative_y=0.75,
                                   vertical_wheel_delta=1,
                                   horizontal_wheel_delta=0),
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'relativeY': 0.75,
                'verticalWheelDelta': 1,
                'horizontalWheelDelta': 0,
            }))

    def test_parses_valid_negative_horizontal_scroll(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=0,
                                   relative_x=0.0,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=-1),
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': -1,
            }))

    def test_parses_valid_positive_horizontal_scroll(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=0,
                                   relative_x=0.0,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=1),
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 1,
            }))

    def test_parses_valid_mouse_event_with_all_buttons_pressed(self):
        self.assertEqual(
            mouse_event.MouseEvent(buttons=31,
                                   relative_x=0.5,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=0),
            mouse_event.parse_mouse_event({
                'buttons': 31,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            }))

    def test_rejects_negative_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': -1,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_too_high_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': 32,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_non_numeric_buttons_value(self):
        with self.assertRaises(mouse_event.InvalidButtonState):
            mouse_event.parse_mouse_event({
                'buttons': 'a',
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_negative_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': -0.001,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_negative_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': -0.001,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_too_high_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 1.001,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_too_high_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 1.001,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_non_float_relative_x_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 'a',
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_non_float_relative_y_value(self):
        with self.assertRaises(mouse_event.InvalidRelativePosition):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 'b',
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_missing_buttons_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'relativeX': 0,
                'relativeY': 0,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_missing_relative_x_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeY': 0,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_missing_relative_y_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_missing_vertical_wheel_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_missing_horizontal_wheel_field(self):
        with self.assertRaises(mouse_event.MissingField):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0,
                'verticalWheelDelta': 0,
            })

    def test_rejects_string_vertical_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 'a',
                'horizontalWheelDelta': 0,
            })

    def test_rejects_float_vertical_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0.5,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_too_high_vertical_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 2,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_too_low_vertical_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': -2,
                'horizontalWheelDelta': 0,
            })

    def test_rejects_string_horizontal_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 'a',
            })

    def test_rejects_float_horizontal_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 0.5,
            })

    def test_rejects_too_high_horizontal_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': 2,
            })

    def test_rejects_too_low_horizontal_wheel_value(self):
        with self.assertRaises(mouse_event.InvalidWheelValue):
            mouse_event.parse_mouse_event({
                'buttons': 0,
                'relativeX': 0.5,
                'relativeY': 0.75,
                'verticalWheelDelta': 0,
                'horizontalWheelDelta': -2,
            })
