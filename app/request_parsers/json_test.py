import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import json


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class JsonParserTest(unittest.TestCase):

    def test_parses_required_fields_from_body(self):
        self.assertEqual(('value-for-a', 'value-for-b'),
                         json.parse_json_body(
                             make_mock_request({
                                 'a': 'value-for-a',
                                 'b': 'value-for-b'
                             }), ['a', 'b']))

    def test_parses_one_required_field_from_body(self):
        self.assertEqual(
            ('field-value',),
            json.parse_json_body(make_mock_request({
                'field': 'field-value',
            }), ['field']))

    def test_parses_different_types(self):
        self.assertEqual(('value-for-a', 52, 27.2, True),
                         json.parse_json_body(
                             make_mock_request({
                                 'a': 'value-for-a',
                                 'b': 52,
                                 'c': 27.2,
                                 'd': True
                             }), ['a', 'b', 'c', 'd']))

    def raises_error_if_malformed_request(self):
        with self.assertRaises(errors.MalformedRequestError):
            json.parse_json_body(make_mock_request(None), ['field'])

    def raises_error_if_missing_required_field(self):
        with self.assertRaises(errors.MissingFieldError):
            json.parse_json_body(
                make_mock_request({
                    'a': 'value-for-a',
                    'b': 'value-for-b'
                }), ['a', 'b', 'c'])
