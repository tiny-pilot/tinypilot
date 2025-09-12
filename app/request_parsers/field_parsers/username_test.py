import unittest

from request_parsers.errors import InvalidUsernameError
from request_parsers.field_parsers import username as username_parser


class ParseUsernameTest(unittest.TestCase):

    def test_rejects_non_string_username(self):
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username(5)
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username(5.4)
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username(None)

    def test_rejects_empty_string_username(self):
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('')

    def test_rejects_too_long_string_username(self):
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('A' * 21)

    def test_rejects_string_with_invalid_characters_username(self):
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username(' joe ')
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('b$b')
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('b@b')
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('b&b')
        with self.assertRaises(InvalidUsernameError):
            username_parser.parse_username('user<script>alert(hi)</script>')

    def test_accepts_single_character_username(self):
        self.assertEqual('b', username_parser.parse_username('b'))

    def test_accepts_username_with_up_to_twenty_characters(self):
        self.assertEqual('this-is-twenty-chars',
                         username_parser.parse_username('this-is-twenty-chars'))

    def test_accepts_username_with_valid_characters(self):
        self.assertEqual('alice', username_parser.parse_username('alice'))
        self.assertEqual('bob', username_parser.parse_username('bob'))
        self.assertEqual('charlie123',
                         username_parser.parse_username('charlie123'))
        self.assertEqual('JAMES', username_parser.parse_username('JAMES'))
        self.assertEqual('bob-foo', username_parser.parse_username('bob-foo'))
        self.assertEqual('bob.foo', username_parser.parse_username('bob.foo'))
        self.assertEqual('bob_foo', username_parser.parse_username('bob_foo'))
