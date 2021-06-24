import unittest

from request_parsers import keystroke

_MODIFIER_PROPS = [
    'metaKey',
    'altKey',
    'shiftKey',
    'ctrlKey',
    'altGraphKey',
]


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

    def test_rejects_invalid_properties(self):
        for invalid_prop in _MODIFIER_PROPS:
            with self.subTest(invalid_prop), self.assertRaises(
                    keystroke.InvalidModifierKeyError):
                props = {
                    'metaKey': False,
                    'altKey': False,
                    'shiftKey': False,
                    'ctrlKey': False,
                    'altGraphKey': False,
                    'key': 'A',
                    'code': 'KeyA',
                }
                props[invalid_prop] = 'banana'
                keystroke.parse_keystroke(props)

    def test_rejects_missing_value(self):
        for missing_prop in _MODIFIER_PROPS + ['code', 'key']:
            with self.subTest(missing_prop), self.assertRaises(
                    keystroke.MissingFieldErrorError):
                props = {
                    'metaKey': False,
                    'altKey': False,
                    'shiftKey': False,
                    'ctrlKey': False,
                    'altGraphKey': False,
                    'key': 'A',
                    'code': 'KeyA',
                }
                del props[missing_prop]
                keystroke.parse_keystroke(props)

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
