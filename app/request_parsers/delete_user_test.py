import unittest
from unittest import mock

from request_parsers import delete_user
from request_parsers import errors


def make_mock_request_json(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class ParseDeleteUserTest(unittest.TestCase):

    def test_parses_valid_delete_username_request(self):
        self.assertEqual(
            'joe',
            delete_user.parse_delete(make_mock_request_json({'username': 'joe'
                                                            })))

    def test_rejects_delete_username_request_with_no_payload(self):
        with self.assertRaises(errors.MalformedRequestError):
            delete_user.parse_delete(make_mock_request_json(json_data=None))

    def test_rejects_delete_username_request_with_no_fields(self):
        with self.assertRaises(errors.MissingFieldError):
            delete_user.parse_delete(make_mock_request_json(json_data={}))

    def test_rejects_delete_username_request_with_empty_username(self):
        with self.assertRaises(errors.InvalidUsernameError):
            delete_user.parse_delete(make_mock_request_json({'username': ''}))

    def test_rejects_delete_username_request_without_username_field(self):
        with self.assertRaises(errors.MissingFieldError):
            delete_user.parse_delete(
                make_mock_request_json({'irrelevantField': 'irrelevantValue'}))
