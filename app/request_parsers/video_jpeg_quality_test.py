import unittest

from request_parsers import errors
from request_parsers import video_jpeg_quality
from request_parsers.test_utils.request import make_mock_request


class VideoJpegQualityParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoJpegQualityError):
            video_jpeg_quality.parse(
                make_mock_request(json_data={'videoJpegQuality': 0}))
        with self.assertRaises(errors.InvalidVideoJpegQualityError):
            video_jpeg_quality.parse(
                make_mock_request(json_data={'videoJpegQuality': 101}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            1,
            video_jpeg_quality.parse(
                make_mock_request(json_data={'videoJpegQuality': 1})))
        self.assertEqual(
            50,
            video_jpeg_quality.parse(
                make_mock_request(json_data={'videoJpegQuality': 50})))
        self.assertEqual(
            100,
            video_jpeg_quality.parse(
                make_mock_request(json_data={'videoJpegQuality': 100})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoJpegQualityError):
                    video_jpeg_quality.parse(
                        make_mock_request(
                            json_data={'videoJpegQuality': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_jpeg_quality.parse(
                make_mock_request(json_data={'jpegQuality': 1}))
