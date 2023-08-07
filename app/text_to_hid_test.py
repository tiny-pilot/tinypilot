import unittest

import text_to_hid
from hid import keycodes as hid


class ConvertTextToHidTest(unittest.TestCase):

    def test_language_mapping(self):
        self.assertEqual((hid.MODIFIER_LEFT_SHIFT, hid.KEYCODE_NUMBER_2),
                         text_to_hid.convert("@", "en-US"))
        self.assertEqual((hid.MODIFIER_LEFT_SHIFT, hid.KEYCODE_SINGLE_QUOTE),
                         text_to_hid.convert("@", "en-GB"))

    def test_defaults_to_enus_language_mapping(self):
        self.assertEqual((hid.MODIFIER_LEFT_SHIFT, hid.KEYCODE_NUMBER_2),
                         text_to_hid.convert("@", "fake-language"))
