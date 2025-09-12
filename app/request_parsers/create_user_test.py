import unittest
from unittest import mock

from request_parsers import create_user
from request_parsers import errors


def make_mock_request_json(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class ParseCreateUserTest(unittest.TestCase):

    def test_accepts_valid_request(self):
        self.assertEqual(('joe', 'dummypass'),
                         create_user.parse(
                             make_mock_request_json({
                                 'username': 'joe',
                                 'password': 'dummypass',
                             })))

    def test_rejects_invalid_field_values(self):
        with self.assertRaises(errors.InvalidUsernameError):
            create_user.parse(
                make_mock_request_json({
                    'username': '$%&@#',
                    'password': 'dummypass',
                }))
        with self.assertRaises(errors.InvalidPasswordError):
            create_user.parse(
                make_mock_request_json({
                    'username': 'joe',
                    'password': 'short',
                }))

    def test_rejects_missing_fields(self):
        with self.assertRaises(errors.MissingFieldError):
            create_user.parse(make_mock_request_json({}))
        with self.assertRaises(errors.MissingFieldError):
            create_user.parse(make_mock_request_json({'username': 'joe'}))
        with self.assertRaises(errors.MissingFieldError):
            create_user.parse(make_mock_request_json({'password': 'dummypass'}))
