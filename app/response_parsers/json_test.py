import json as json_encoder
import unittest
from unittest import mock

from response_parsers import errors
from response_parsers import json


def make_mock_response(json_data):
    mock_response = mock.Mock()
    mock_response.read.return_value = json_encoder.dumps(json_data).encode()
    return mock_response


class JsonParserTest(unittest.TestCase):

    def test_parses_required_fields_from_body(self):
        mock_response = make_mock_response({
            'a': 'value-for-a',
            'b': 'value-for-b'
        })
        self.assertEqual(('value-for-a', 'value-for-b'),
                         json.parse_json_body(mock_response, ['a', 'b']))

    def test_parses_one_required_field_from_body(self):
        mock_response = make_mock_response({
            'field': 'field-value',
        })
        self.assertEqual(('field-value',),
                         json.parse_json_body(mock_response, ['field']))

    def test_parses_with_no_required_field(self):
        mock_response = make_mock_response({
            'field': 'field-value',
        })
        self.assertEqual((), json.parse_json_body(mock_response, []))

    def test_parses_with_less_required_fields_than_actual_fields_in_body(self):
        mock_response = make_mock_response({
            'a': 'value-for-a',
            'b': 'value-for-b',
            'c': 'value-for-c',
        })
        self.assertEqual(('value-for-a', 'value-for-c'),
                         json.parse_json_body(mock_response, ['a', 'c']))

    def test_parses_different_types(self):
        mock_response = make_mock_response({
            'a': 'value-for-a',
            'b': 52,
            'c': 27.2,
            'd': True
        })
        self.assertEqual(('value-for-a', 52, 27.2, True),
                         json.parse_json_body(mock_response,
                                              ['a', 'b', 'c', 'd']))

    def raises_error_if_malformed_response(self):
        mock_response = make_mock_response(None)
        with self.assertRaises(errors.MalformedResponseError):
            json.parse_json_body(mock_response, ['field'])

    def raises_error_if_missing_required_field(self):
        mock_response = make_mock_response({
            'a': 'value-for-a',
            'b': 'value-for-b'
        })
        with self.assertRaises(errors.MissingFieldError):
            json.parse_json_body(mock_response, ['a', 'b', 'c'])
