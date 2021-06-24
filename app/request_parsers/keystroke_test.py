import unittest

from request_parsers import keystroke


class KeystrokeTest(unittest.TestCase):

    # Intentionally violating style conventions sot hat we can parallel the
    # self.assertEqual method.
    # pylint: disable=no-self-use
    # pylint: disable=invalid-name
    def assertKeystrokesEqual(self, expected, actual):
        if expected != actual:
            raise AssertionError('%s != %s' % (expected, actual))

    def test_parses_valid_keystroke_message(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_ctrl_modifier=False,
                                key='A',
                                code='KeyA'),
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            }))

    def test_parses_valid_keystroke_message_with_all_modifiers_pushed(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=True,
                                right_meta_modifier=True,
                                left_alt_modifier=True,
                                right_alt_modifier=True,
                                left_shift_modifier=True,
                                right_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_ctrl_modifier=True,
                                key='A',
                                code='KeyA'),
            keystroke.parse_keystroke({
                'metaLeft': True,
                'metaRight': True,
                'shiftLeft': True,
                'shiftRight': True,
                'altLeft': True,
                'altRight': True,
                'ctrlLeft': True,
                'ctrlRight': True,
                'key': 'A',
                'code': 'KeyA',
            }))

    def test_parses_left_ctrl_key(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_ctrl_modifier=False,
                                key='Control',
                                code='ControlLeft'),
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': True,
                'ctrlRight': False,
                'key': 'Control',
                'code': 'ControlLeft',
            }))

    def test_parses_right_ctrl_key(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_ctrl_modifier=True,
                                key='Control',
                                code='ControlRight'),
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': True,
                'key': 'Control',
                'code': 'ControlRight',
            }))

    def test_rejects_float_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCodeError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 1.25,
            })

    def test_rejects_too_long_code_value(self):
        with self.assertRaises(keystroke.InvalidKeyCodeError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'A' * 31,
            })


class KeystrokeWithInvalidValuesTest(unittest.TestCase):

    def test_rejects_invalid_meta_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaLeft': 'banana',
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_alt_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': 'banana',
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_right_alt_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': 'banana',
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_shift_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': 'banana',
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_ctrl_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': 'banana',
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })


class KeystrokeWithMissingFieldsTest(unittest.TestCase):

    def test_rejects_missing_meta_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_alt_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_right_alt_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_shift_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_ctrl_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlRight': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'code': 'KeyA',
            })

    def test_rejects_missing_code_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaLeft': False,
                'metaRight': False,
                'shiftLeft': False,
                'shiftRight': False,
                'altLeft': False,
                'altRight': False,
                'ctrlLeft': False,
                'ctrlRight': False,
                'key': 'A',
            })
