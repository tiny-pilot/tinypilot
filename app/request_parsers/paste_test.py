import unittest
from unittest import mock

from hid import keycodes as hid
from request_parsers import errors
from request_parsers import paste


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class KeystrokesParserTest(unittest.TestCase):

    def test_accepts(self):
        self.assertEqual([
            hid.Keystroke(keycode=hid.KEYCODE_A),
            hid.Keystroke(keycode=hid.KEYCODE_B),
            hid.Keystroke(keycode=hid.KEYCODE_C),
        ],
                         paste.parse_keystrokes(
                             make_mock_request({
                                 'text': 'abc',
                                 'language': 'en-US'
                             })))

    def test_rejects_unsupported_character(self):
        with self.assertRaises(errors.UnsupportedPastedCharacterError) as ctx:
            paste.parse_keystrokes(
                make_mock_request({
                    'text': '“',
                    'language': 'en-US'
                }))
        self.assertEqual('This character is not supported: “',
                         str(ctx.exception))
