import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import requires_https


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class RequiresHttpsTest(unittest.TestCase):

    def test_accept_valid_values(self):
        self.assertTrue(
            requires_https.parse(make_mock_request({'requiresHttps': True})))
        self.assertFalse(
            requires_https.parse(make_mock_request({'requiresHttps': False})))

    def test_rejects_absent_value(self):
        with self.assertRaises(errors.MissingFieldError):
            requires_https.parse(make_mock_request({}))

    def test_rejects_invalid_values(self):
        with self.assertRaises(errors.InvalidRequiresHttpsPropError):
            requires_https.parse(make_mock_request({'requiresHttps': 1}))

        with self.assertRaises(errors.InvalidRequiresHttpsPropError):
            requires_https.parse(make_mock_request({'requiresHttps': None}))

        with self.assertRaises(errors.InvalidRequiresHttpsPropError):
            requires_https.parse(make_mock_request({'requiresHttps': 'true'}))
