import unittest

from hid.keycodes import azerty
from hid.keycodes import modifiers
from hid.keycodes import qwerty
from js_to_hid import convert
from request_parsers import keystroke


class ConvertJsToHIDTest(unittest.TestCase):

    def test_converts_simple_qwerty_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='a',
                                key_code=65,
                                is_left_modifier=False), 'qwerty')
        self.assertEqual(0, modifier_bitmask)
        self.assertEqual(qwerty.KEYCODE_A, hid_keycode)

    def test_converts_shifted_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=True,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='A',
<<<<<<< HEAD
                                key_code=65), 'qwerty')
        self.assertEqual(modifiers.LEFT_SHIFT, modifier_bitmask)
        self.assertEqual(qwerty.KEYCODE_A, hid_keycode)

    def test_converts_keystroke_with_all_modifiers_pressed(self):
=======
                                key_code=65,
                                is_left_modifier=False), 'qwerty')
        self.assertEqual(0x02, modifier_bitmask)
        self.assertEqual(qwerty.KEYCODE_A, hid_keycode)

    def test_converts_keystroke_with_all_modifier_bitmask_pressed(self):
>>>>>>> Add support for right modifier keys
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=True,
                                left_alt_modifier=True,
                                left_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_alt_modifier=True,
                                key='A',
<<<<<<< HEAD
                                key_code=65), 'qwerty')
        self.assertEqual(
            modifiers.LEFT_META | modifiers.LEFT_ALT | modifiers.LEFT_SHIFT |
            modifiers.LEFT_CTRL | modifiers.RIGHT_ALT, modifier_bitmask)
=======
                                key_code=65,
                                is_left_modifier=False), 'qwerty')
        self.assertEqual(0x4f, modifier_bitmask)
>>>>>>> Add support for right modifier keys
        self.assertEqual(qwerty.KEYCODE_A, hid_keycode)

    def test_converts_left_ctrl_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_alt_modifier=False,
                                key='Control',
                                key_code=17,
                                is_left_modifier=True), 'qwerty')
        self.assertEqual(modifiers.LEFT_CTRL, modifier_bitmask)
        self.assertEqual(qwerty.KEYCODE_LEFT_CTRL, hid_keycode)

    def test_converts_right_ctrl_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_alt_modifier=False,
                                key='Control',
                                key_code=17,
                                is_left_modifier=False), 'qwerty')
        self.assertEqual(modifiers.LEFT_CTRL, modifier_bitmask)
        self.assertEqual(qwerty.KEYCODE_RIGHT_CTRL, hid_keycode)

    def test_converts_simple_azerty_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='a',
                                key_code=65,
                                is_left_modifier=False), 'azerty')
        self.assertEqual(0, modifier_bitmask)
        self.assertEqual(azerty.KEYCODE_A, hid_keycode)
