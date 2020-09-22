import unittest

from request_parsers import keystroke


class Keystroke:
    id: int
    meta_modifier: bool
    alt_modifier: bool
    shift_modifier: bool
    ctrl_modifier: bool
    key: str
    key_code: int


class KeystrokeTest(unittest.TestCase):

    def test_parses_valid_keystroke_message(self):
        self.assertEqual(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='A',
                                key_code=65),
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 65,
            }))

    def test_parses_valid_keystroke_message_with_all_modifiers_pushed(self):
        self.assertEqual(
            keystroke.Keystroke(left_meta_modifier=True,
                                left_alt_modifier=True,
                                left_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_alt_modifier=True,
                                key='A',
                                key_code=65),
            keystroke.parse_keystroke({
                'metaKey': True,
                'altKey': True,
                'shiftKey': True,
                'ctrlKey': True,
                'altGraphKey': True,
                'key': 'A',
                'keyCode': 65,
            }))

    def test_rejects_invalid_meta_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'metaKey': 'banana',
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_alt_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': 'banana',
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_shift_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': 'banana',
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_ctrl_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': 'banana',
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_alt_graph_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': 'banana',
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_negative_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': -1,
            })

    def test_rejects_too_high_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 0xff + 1,
            })

    def test_rejects_string_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 'banana',
            })

    def test_rejects_float_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 1.25,
            })

    def test_rejects_missing_meta_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_alt_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_alt_graph_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'altKey': False,
                'metaKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_shift_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_ctrl_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'altGraphKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'keyCode': 1,
            })

    def test_rejects_missing_key_code_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
            })
