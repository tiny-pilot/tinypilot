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
            keystroke.Keystroke(id=123,
                                meta_modifier=False,
                                alt_modifier=False,
                                shift_modifier=False,
                                ctrl_modifier=False,
                                key='A',
                                key_code=65),
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 65,
            }))

    def test_parses_valid_keystroke_message_with_all_modifiers_pushed(self):
        self.assertEqual(
            keystroke.Keystroke(id=456,
                                meta_modifier=True,
                                alt_modifier=True,
                                shift_modifier=True,
                                ctrl_modifier=True,
                                key='A',
                                key_code=65),
            keystroke.parse_keystroke({
                'id': 456,
                'metaKey': True,
                'altKey': True,
                'shiftKey': True,
                'ctrlKey': True,
                'key': 'A',
                'keyCode': 65,
            }))

    def test_rejects_invalid_meta_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': 'banana',
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_alt_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': 'banana',
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_shift_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': 'banana',
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_invalid_ctrl_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKey):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': 'banana',
                'key': 'A',
                'keyCode': 65,
            })

    def test_rejects_negative_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': -1,
            })

    def test_rejects_too_high_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 0xff + 1,
            })

    def test_rejects_string_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 'banana',
            })

    def test_rejects_float_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCode):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1.25,
            })

    def test_rejects_missing_id_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_meta_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_alt_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_shift_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'ctrlKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_ctrl_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'key': 'A',
                'keyCode': 1,
            })

    def test_rejects_missing_key_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'keyCode': 1,
            })

    def test_rejects_missing_key_code_value(self):
        with self.assertRaises(keystroke.MissingField):
            keystroke.parse_keystroke({
                'id': 123,
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
            })
