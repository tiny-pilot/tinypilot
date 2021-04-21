import unittest
from unittest import mock

from request_parsers import errors
from request_parsers import video_fps


def _make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class VideoFpsParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoFpsError):
            video_fps.parse(_make_mock_request({'videoFps': 0}))
        with self.assertRaises(errors.InvalidVideoFpsError):
            video_fps.parse(_make_mock_request({'videoFps': 31}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(1,
                         video_fps.parse(_make_mock_request({'videoFps': 1})))
        self.assertEqual(15,
                         video_fps.parse(_make_mock_request({'videoFps': 15})))
        self.assertEqual(30,
                         video_fps.parse(_make_mock_request({'videoFps': 30})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoFpsError):
                    video_fps.parse(_make_mock_request({'videoFps': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_fps.parse(_make_mock_request({'fps': 1}))
