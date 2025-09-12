import unittest

from request_parsers import errors
from request_parsers.field_parsers import password as password_parser


class ParsePasswordTest(unittest.TestCase):

    def test_rejects_non_string_password(self):
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password(5)
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password(5.4)
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password(None)

    def test_rejects_empty_string_password(self):
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password('')

    def test_rejects_too_long_string_password(self):
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password('A' * 61)

    def test_rejects_too_short_string_password(self):
        with self.assertRaises(errors.InvalidPasswordError):
            password_parser.parse_password('A' * 5)

    def test_accepts_standard_passwords(self):
        self.assertEqual('dummypass',
                         password_parser.parse_password('dummypass'))
        self.assertEqual('pass123', password_parser.parse_password('pass123'))
        self.assertEqual('My P@ssw0rd!1!11',
                         password_parser.parse_password('My P@ssw0rd!1!11'))
