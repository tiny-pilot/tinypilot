import unittest

import js_to_hid
from hid import keycodes as hid
from request_parsers import keystroke


class ConvertJsToHIDTest(unittest.TestCase):

    def test_converts_simple_keystroke(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_ctrl_modifier=False,
                                key='a',
                                code='KeyA'))
        self.assertEqual(hid.Keystroke(keycode=hid.KEYCODE_A), hid_keystroke)

    def test_converts_shifted_keystroke(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=True,
                                right_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_ctrl_modifier=False,
                                key='A',
                                code='KeyA'))
        self.assertEqual(
            hid.Keystroke(keycode=hid.KEYCODE_A,
                          modifier=hid.MODIFIER_LEFT_SHIFT), hid_keystroke)

    def test_converts_keystroke_with_all_modifiers_pressed(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=True,
                                right_meta_modifier=True,
                                left_alt_modifier=True,
                                right_alt_modifier=True,
                                left_shift_modifier=True,
                                right_shift_modifier=True,
                                left_ctrl_modifier=True,
                                right_ctrl_modifier=True,
                                key='A',
                                code='KeyA'))
        self.assertEqual(
            hid.Keystroke(
                keycode=hid.KEYCODE_A,
                modifier=(hid.MODIFIER_LEFT_META | hid.MODIFIER_RIGHT_META |
                          hid.MODIFIER_LEFT_ALT | hid.MODIFIER_RIGHT_ALT |
                          hid.MODIFIER_LEFT_SHIFT | hid.MODIFIER_RIGHT_SHIFT |
                          hid.MODIFIER_LEFT_CTRL | hid.MODIFIER_RIGHT_CTRL)),
            hid_keystroke)

    def test_converts_left_ctrl_keystroke(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_ctrl_modifier=False,
                                key='Control',
                                code='ControlLeft'))
        self.assertEqual(
            hid.Keystroke(keycode=hid.KEYCODE_NONE,
                          modifier=hid.MODIFIER_LEFT_CTRL), hid_keystroke)

    def test_converts_right_ctrl_keystroke(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=False,
                                right_shift_modifier=False,
                                left_ctrl_modifier=False,
                                right_ctrl_modifier=True,
                                key='Control',
                                code='ControlRight'))
        self.assertEqual(
            hid.Keystroke(keycode=hid.KEYCODE_NONE,
                          modifier=hid.MODIFIER_RIGHT_CTRL), hid_keystroke)

    def test_converts_left_ctrl_with_shift_left_keystroke(self):
        hid_keystroke = js_to_hid.convert(
            keystroke.Keystroke(left_meta_modifier=False,
                                right_meta_modifier=False,
                                left_alt_modifier=False,
                                right_alt_modifier=False,
                                left_shift_modifier=True,
                                right_shift_modifier=False,
                                left_ctrl_modifier=True,
                                right_ctrl_modifier=False,
                                key='Control',
                                code='ControlLeft'))
        self.assertEqual(
            hid.Keystroke(keycode=hid.KEYCODE_LEFT_CTRL,
                          modifier=(hid.MODIFIER_LEFT_CTRL |
                                    hid.MODIFIER_LEFT_SHIFT)), hid_keystroke)

    def test_raises_exception_on_unrecognized_code(self):
        with self.assertRaises(js_to_hid.UnrecognizedKeyCodeError):
            js_to_hid.convert(
                keystroke.Keystroke(left_meta_modifier=False,
                                    right_meta_modifier=False,
                                    left_alt_modifier=False,
                                    right_alt_modifier=False,
                                    left_shift_modifier=False,
                                    right_shift_modifier=False,
                                    left_ctrl_modifier=False,
                                    right_ctrl_modifier=False,
                                    key='a',
                                    code='MadeUpInvalidCode'))

    def test_raises_exception_on_blank_code(self):
        with self.assertRaises(js_to_hid.UnrecognizedKeyCodeError):
            js_to_hid.convert(
                keystroke.Keystroke(left_meta_modifier=False,
                                    right_meta_modifier=False,
                                    left_alt_modifier=False,
                                    right_alt_modifier=False,
                                    left_shift_modifier=False,
                                    right_shift_modifier=False,
                                    left_ctrl_modifier=False,
                                    right_ctrl_modifier=False,
                                    key='a',
                                    code=''))
