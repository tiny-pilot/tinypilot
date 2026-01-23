import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import password


def make_mock_request_json(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class ParsePasswordTest(unittest.TestCase):

    def test_accepts_valid_request(self):
        self.assertEqual(
            'dummypass',
            password.parse_password(
                make_mock_request_json({'password': 'dummypass'})))

    def test_rejects_invalid_password(self):
        with self.assertRaises(errors.InvalidPasswordError):
            password.parse_password(
                make_mock_request_json({'password': 'short'}))

    def test_rejects_missing_password_field(self):
        with self.assertRaises(errors.MissingFieldError):
            password.parse_password(make_mock_request_json({}))
