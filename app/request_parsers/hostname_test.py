import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import hostname


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class HostnameValidationTest(unittest.TestCase):

    def test_accepts_hostname_with_valid_characters(self):
        hostname_valid = 'tiny-pilot123'
        self.assertEqual(
            hostname_valid,
            hostname.parse_hostname(
                make_mock_request({'hostname': hostname_valid})))

    def test_accepts_hostname_with_exactly_63_characters(self):
        hostname_63_chars = 'a' * 63
        self.assertEqual(
            hostname_63_chars,
            hostname.parse_hostname(
                make_mock_request({'hostname': hostname_63_chars})))

    def test_rejects_hostname_that_is_not_a_string(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': 1}))
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': None}))

    def test_rejects_hostnames_with_invalid_characters(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': 'TINYPILOT'
                                                      }))
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(
                make_mock_request({'hostname': 'tinypilot***'}))
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(
                make_mock_request({'hostname': 'tiny.pilot'}))

    def test_rejects_localhost_as_hostname(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': 'localhost'
                                                      }))

    def test_rejects_empty_hostname(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': ''}))

    def test_rejects_hostname_that_is_longer_than_63_chars(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': 'a' * 64}))

    def test_rejects_hostname_that_starts_with_a_dash(self):
        with self.assertRaises(errors.InvalidHostnameError):
            hostname.parse_hostname(make_mock_request({'hostname': '-invalid'}))
