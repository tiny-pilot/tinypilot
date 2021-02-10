import unittest

from hid import keycodes as hid
from js_to_hid import convert
from request_parsers import keystroke


class ConvertJsToHIDTest(unittest.TestCase):

    def test_converts_simple_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='a',
                                code='KeyA'))
        self.assertEqual(0, modifier_bitmask)
        self.assertEqual(hid.KEYCODE_A, hid_keycode)

    def test_converts_shifted_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=True,
                                left_ctrl_modifier=False,
                                right_alt_modifier=False,
                                key='A',
                                code='KeyA'))
        self.assertEqual(hid.MODIFIER_LEFT_SHIFT, modifier_bitmask)
        self.assertEqual(hid.KEYCODE_A, hid_keycode)

    def test_converts_keystroke_with_all_modifiers_pressed(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=True,
                                left_alt_modifier=True,
                                left_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_alt_modifier=True,
                                key='A',
                                code='KeyA'))
        self.assertEqual(
            hid.MODIFIER_LEFT_META | hid.MODIFIER_LEFT_ALT |
            hid.MODIFIER_LEFT_SHIFT | hid.MODIFIER_LEFT_CTRL |
            hid.MODIFIER_RIGHT_ALT, modifier_bitmask)
        self.assertEqual(hid.KEYCODE_A, hid_keycode)

    def test_converts_left_ctrl_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_alt_modifier=False,
                                key='Control',
                                code='ControlLeft'))
        self.assertEqual(hid.MODIFIER_LEFT_CTRL, modifier_bitmask)
        self.assertEqual(hid.KEYCODE_LEFT_CTRL, hid_keycode)

    def test_converts_right_ctrl_keystroke(self):
        modifier_bitmask, hid_keycode = convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                left_alt_modifier=False,
                                left_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_alt_modifier=False,
                                key='Control',
                                code='ControlRight'))
        self.assertEqual(hid.MODIFIER_RIGHT_CTRL, modifier_bitmask)
        self.assertEqual(hid.KEYCODE_RIGHT_CTRL, hid_keycode)
