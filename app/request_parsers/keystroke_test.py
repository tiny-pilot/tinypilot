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
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='A',
                                code='KeyA'),
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            }))

    def test_parses_valid_keystroke_message_with_all_modifiers_pushed(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=True,
                                left_alt_modifier=True,
                                left_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_alt_modifier=True,
                                key='A',
                                code='KeyA'),
            keystroke.parse_keystroke({
                'metaKey': True,
                'altKey': True,
                'shiftKey': True,
                'ctrlKey': True,
                'altGraphKey': True,
                'key': 'A',
                'code': 'KeyA',
            }))

    def test_parses_left_ctrl_key(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_alt_modifier=False,
                                key='Control',
                                code='ControlLeft'),
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': True,
                'altGraphKey': False,
                'key': 'Control',
                'code': 'ControlLeft',
            }))

    def test_parses_right_ctrl_key(self):
        self.assertKeystrokesEqual(
            keystroke.Keystroke(
                left_meta_modifier=False,
                left_alt_modifier=False,
                left_shift_modifier=False,
                # For simplicity, we store right Ctrl modifier in
                # left_ctrl_modifier since there's no right version in
                # keystroke.Keystroke.
                left_ctrl_modifier=True,
                right_alt_modifier=False,
                key='Control',
                code='ControlRight'),
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': True,
                'altGraphKey': False,
                'key': 'Control',
                'code': 'ControlRight',
            }))

    def test_rejects_float_keycode_value(self):
        with self.assertRaises(keystroke.InvalidKeyCodeError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 1.25,
            })

    def test_rejects_too_long_code_value(self):
        with self.assertRaises(keystroke.InvalidKeyCodeError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'A' * 31,
            })


class KeystrokeWithInvalidValuesTest(unittest.TestCase):

    def test_rejects_invalid_meta_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaKey': 'banana',
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_alt_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': 'banana',
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_shift_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': 'banana',
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_ctrl_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': 'banana',
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_invalid_alt_graph_modifier(self):
        with self.assertRaises(keystroke.InvalidModifierKeyError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': 'banana',
                'key': 'A',
                'code': 'KeyA',
            })


class KeystrokeWithMissingFieldsTest(unittest.TestCase):

    def test_rejects_missing_meta_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_alt_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_alt_graph_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'altKey': False,
                'metaKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_shift_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_ctrl_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'altGraphKey': False,
                'key': 'A',
                'code': 'KeyA',
            })

    def test_rejects_missing_key_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'code': 'KeyA',
            })

    def test_rejects_missing_code_value(self):
        with self.assertRaises(keystroke.MissingFieldErrorError):
            keystroke.parse_keystroke({
                'metaKey': False,
                'altKey': False,
                'shiftKey': False,
                'ctrlKey': False,
                'altGraphKey': False,
                'key': 'A',
            })
