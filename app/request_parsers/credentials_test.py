import unittest
from unittest import mock

from request_parsers import credentials
from request_parsers import errors


def make_mock_request_json(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class ParseCredentialsTest(unittest.TestCase):

    def test_accepts_valid_request(self):
        self.assertEqual(('joe', 'dummypass'),
                         credentials.parse_credentials(
                             make_mock_request_json({
                                 'username': 'joe',
                                 'password': 'dummypass'
                             })))

    def test_rejects_invalid_field_values(self):
        with self.assertRaises(errors.InvalidUsernameError):
            credentials.parse_credentials(
                make_mock_request_json({
                    'username': '$%&@#',
                    'password': 'dummypass'
                }))
        with self.assertRaises(errors.InvalidPasswordError):
            credentials.parse_credentials(
                make_mock_request_json({
                    'username': 'joe',
                    'password': 'short'
                }))

    def test_rejects_missing_fields(self):
        with self.assertRaises(errors.MissingFieldError):
            credentials.parse_credentials(make_mock_request_json({}))
        with self.assertRaises(errors.MissingFieldError):
            credentials.parse_credentials(
                make_mock_request_json({'username': 'joe'}))
        with self.assertRaises(errors.MissingFieldError):
            credentials.parse_credentials(
                make_mock_request_json({'password': 'dummypass'}))
