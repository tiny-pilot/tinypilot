import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import invert_scroll_direction


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class InvertScrollDirectionTest(unittest.TestCase):

    def test_accept_valid_values(self):
        self.assertTrue(
            invert_scroll_direction.parse(
                make_mock_request({'invertScrollDirection': True})))
        self.assertFalse(
            invert_scroll_direction.parse(
                make_mock_request({'invertScrollDirection': False})))

    def test_rejects_absent_value(self):
        with self.assertRaises(errors.MissingFieldError):
            invert_scroll_direction.parse(make_mock_request({}))

    def test_rejects_invalid_values(self):
        with self.assertRaises(errors.InvalidInvertScrollDirectionPropError):
            invert_scroll_direction.parse(
                make_mock_request({'invertScrollDirection': 1}))

        with self.assertRaises(errors.InvalidInvertScrollDirectionPropError):
            invert_scroll_direction.parse(
                make_mock_request({'invertScrollDirection': None}))

        with self.assertRaises(errors.InvalidInvertScrollDirectionPropError):
            invert_scroll_direction.parse(
                make_mock_request({'invertScrollDirection': 'true'}))
