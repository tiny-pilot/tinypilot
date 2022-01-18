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
        mock_request = make_mock_request({
            'a': 'value-for-a',
            'b': 'value-for-b'
        })
        self.assertEqual(('value-for-a', 'value-for-b'),
                         json.parse_json_body(mock_request, ['a', 'b']))

    def test_parses_one_required_field_from_body(self):
        mock_request = make_mock_request({
            'field': 'field-value',
        })
        self.assertEqual(('field-value',),
                         json.parse_json_body(mock_request, ['field']))

    def test_parses_with_no_required_field(self):
        mock_request = make_mock_request({
            'field': 'field-value',
        })
        self.assertEqual((), json.parse_json_body(mock_request, []))

    def test_parses_with_less_required_fields_than_actual_fields_in_body(self):
        mock_request = make_mock_request({
            'a': 'value-for-a',
            'b': 'value-for-b',
            'c': 'value-for-c',
        })
        self.assertEqual(('value-for-a', 'value-for-c'),
                         json.parse_json_body(mock_request, ['a', 'c']))

    def test_parses_different_types(self):
        mock_request = make_mock_request({
            'a': 'value-for-a',
            'b': 52,
            'c': 27.2,
            'd': True
        })
        self.assertEqual(('value-for-a', 52, 27.2, True),
                         json.parse_json_body(mock_request,
                                              ['a', 'b', 'c', 'd']))

    def raises_error_if_malformed_request(self):
        mock_request = make_mock_request(None)
        with self.assertRaises(errors.MalformedRequestError):
            json.parse_json_body(mock_request, ['field'])

    def raises_error_if_missing_required_field(self):
        mock_request = make_mock_request({
            'a': 'value-for-a',
            'b': 'value-for-b'
        })
        with self.assertRaises(errors.MissingFieldError):
            json.parse_json_body(mock_request, ['a', 'b', 'c'])
