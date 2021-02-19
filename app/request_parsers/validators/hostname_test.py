import unittest

from request_parsers.validators import hostname


class HostnameValidationTest(unittest.TestCase):

    def test_accepts_hostname_with_valid_characters(self):
        self.assertTrue(hostname.validate('tiny-pilot123'))

    def test_accepts_hostname_with_exactly_63_characters(self):
        self.assertTrue(hostname.validate('a' * 63))

    def test_rejects_hostname_that_is_not_a_string(self):
        self.assertFalse(hostname.validate(1))
        self.assertFalse(hostname.validate(None))

    def test_rejects_hostnames_with_invalid_characters(self):
        self.assertFalse(hostname.validate('TINYPILOT'))
        self.assertFalse(hostname.validate('tinypilot***'))
        self.assertFalse(hostname.validate('tiny.pilot'))

    def test_rejects_localhost_as_hostname(self):
        self.assertFalse(hostname.validate('localhost'))

    def test_rejects_empty_hostname(self):
        self.assertFalse(hostname.validate(''))

    def test_rejects_hostname_that_is_longer_than_63_chars(self):
        self.assertFalse(hostname.validate('a' * 64))

    def test_rejects_hostname_that_starts_with_a_dash(self):
        self.assertFalse(hostname.validate('-invalid'))
