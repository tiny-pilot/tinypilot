import unittest

from request_parsers.validators import hostname


class MyTestCase(unittest.TestCase):

    def test_accepts_hostname_with_valid_characters(self):
        self.assertEqual(hostname.validate('tiny-pilot123'), True)

    def test_accepts_hostname_with_exactly_63_characters(self):
        self.assertEqual(hostname.validate('a' * 63), True)

    def test_rejects_hostname_that_is_not_a_string(self):
        self.assertEqual(hostname.validate(1), False)

    def test_rejects_hostnames_with_invalid_characters(self):
        self.assertEqual(hostname.validate('TINYPILOT'), False)
        self.assertEqual(hostname.validate('tinypilot***'), False)
        self.assertEqual(hostname.validate('tiny.pilot'), False)

    def test_rejects_empty_hostname(self):
        self.assertEqual(hostname.validate(''), False)

    def test_rejects_hostname_that_is_longer_than_63_chars(self):
        self.assertEqual(hostname.validate('a' * 64), False)

    def test_rejects_hostname_that_starts_with_a_dash(self):
        self.assertEqual(hostname.validate('-invalid'), False)
