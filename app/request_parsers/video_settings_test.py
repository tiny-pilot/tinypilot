import unittest
from unittest import mock

import db.settings
from request_parsers import errors
from request_parsers import video_settings


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class VideoFpsParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoFpsError):
            video_settings.parse_fps(make_mock_request({'videoFps': 0}))
        with self.assertRaises(errors.InvalidVideoFpsError):
            video_settings.parse_fps(make_mock_request({'videoFps': 31}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            1, video_settings.parse_fps(make_mock_request({'videoFps': 1})))
        self.assertEqual(
            15, video_settings.parse_fps(make_mock_request({'videoFps': 15})))
        self.assertEqual(
            30, video_settings.parse_fps(make_mock_request({'videoFps': 30})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoFpsError):
                    video_settings.parse_fps(
                        make_mock_request({'videoFps': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_fps(make_mock_request({'fps': 1}))


class VideoJpegQualityParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoJpegQualityError):
            video_settings.parse_jpeg_quality(
                make_mock_request({'videoJpegQuality': 0}))
        with self.assertRaises(errors.InvalidVideoJpegQualityError):
            video_settings.parse_jpeg_quality(
                make_mock_request({'videoJpegQuality': 101}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            1,
            video_settings.parse_jpeg_quality(
                make_mock_request({'videoJpegQuality': 1})))
        self.assertEqual(
            50,
            video_settings.parse_jpeg_quality(
                make_mock_request({'videoJpegQuality': 50})))
        self.assertEqual(
            100,
            video_settings.parse_jpeg_quality(
                make_mock_request({'videoJpegQuality': 100})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoJpegQualityError):
                    video_settings.parse_jpeg_quality(
                        make_mock_request({'videoJpegQuality': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_jpeg_quality(
                make_mock_request({'jpegQuality': 1}))


class VideoH264BitrateParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoH264BitrateError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'videoH264Bitrate': 24}))
        with self.assertRaises(errors.InvalidVideoH264BitrateError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'videoH264Bitrate': 20001}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            25,
            video_settings.parse_h264_bitrate(
                make_mock_request({'videoH264Bitrate': 25})))
        self.assertEqual(
            5000,
            video_settings.parse_h264_bitrate(
                make_mock_request({'videoH264Bitrate': 5000})))
        self.assertEqual(
            20000,
            video_settings.parse_h264_bitrate(
                make_mock_request({'videoH264Bitrate': 20000})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoH264BitrateError):
                    video_settings.parse_h264_bitrate(
                        make_mock_request({'videoH264Bitrate': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 1}))


class VideoStreamingModeParserTest(unittest.TestCase):

    def test_accept_valid_values(self):
        self.assertEqual(
            db.settings.StreamingMode.MJPEG,
            video_settings.parse_streaming_mode(
                make_mock_request({'videoStreamingMode': 'MJPEG'})))
        self.assertEqual(
            db.settings.StreamingMode.H264,
            video_settings.parse_streaming_mode(
                make_mock_request({'videoStreamingMode': 'H264'})))

    def test_reject_invalid_modes(self):
        with self.assertRaises(errors.InvalidVideoStreamingModeError):
            video_settings.parse_streaming_mode(
                make_mock_request({'videoStreamingMode': 'mjpeg'}))
        with self.assertRaises(errors.InvalidVideoStreamingModeError):
            video_settings.parse_streaming_mode(
                make_mock_request({'videoStreamingMode': 'asdf'}))

    def test_reject_invalid_types(self):
        for value in [None, True, 15.0, (), [], {}]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoStreamingModeError):
                    video_settings.parse_streaming_mode(
                        make_mock_request({'videoStreamingMode': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_streaming_mode(
                make_mock_request({'streamingMode': 'MJPEG'}))
