import unittest

import text_to_hid
from hid import keycodes as hid


class ConvertTextToHidTest(unittest.TestCase):

    def test_keystroke_without_modifier(self):
        self.assertEqual(hid.Keystroke(keycode=hid.KEYCODE_A),
                         text_to_hid.convert('a', 'en-US'))

    def test_keystroke_with_modifier(self):
        self.assertEqual(
            hid.Keystroke(keycode=hid.KEYCODE_A,
                          modifier=hid.MODIFIER_LEFT_SHIFT),
            text_to_hid.convert('A', 'en-US'))

    def test_language_mapping(self):
        self.assertEqual(
            hid.Keystroke(hid.KEYCODE_NUMBER_2, hid.MODIFIER_LEFT_SHIFT),
            text_to_hid.convert('@', 'en-US'))
        self.assertEqual(
            hid.Keystroke(hid.KEYCODE_SINGLE_QUOTE, hid.MODIFIER_LEFT_SHIFT),
            text_to_hid.convert('@', 'en-GB'))

    def test_defaults_to_us_english_language_mapping(self):
        self.assertEqual(
            hid.Keystroke(hid.KEYCODE_NUMBER_2, hid.MODIFIER_LEFT_SHIFT),
            text_to_hid.convert('@', 'fake-language'))

    def test_raises_error_on_unsupported_character(self):
        with self.assertRaises(text_to_hid.UnsupportedCharacterError):
            text_to_hid.convert('\r', 'en-US')
