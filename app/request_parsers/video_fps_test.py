import unittest
from unittest import mock

from request_parsers import video_fps
from request_parsers.errors import InvalidVideoFpsError
from request_parsers.errors import MissingFieldError


class VideoFpsParserTest(unittest.TestCase):

    def make_mock_request(self, json_data):
        patcher = mock.patch('flask.request')
        self.addCleanup(patcher.stop)
        mock_request = patcher.start()
        mock_request.get_json.return_value = json_data
        return mock_request

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(InvalidVideoFpsError):
            video_fps.parse(self.make_mock_request({'videoFps': 0}))
        with self.assertRaises(InvalidVideoFpsError):
            video_fps.parse(self.make_mock_request({'videoFps': 31}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            video_fps.parse(self.make_mock_request({'videoFps': 1})), 1)
        self.assertEqual(
            video_fps.parse(self.make_mock_request({'videoFps': 15})), 15)
        self.assertEqual(
            video_fps.parse(self.make_mock_request({'videoFps': 30})), 30)

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(InvalidVideoFpsError):
                    video_fps.parse(self.make_mock_request({'videoFps': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(MissingFieldError):
            video_fps.parse(self.make_mock_request({'fps': 1}))
