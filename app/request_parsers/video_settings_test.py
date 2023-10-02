import unittest
from unittest import mock

import db.settings
from request_parsers import errors
from request_parsers import video_settings


def make_mock_request(json_data):
    mock_request = mock.Mock()
    mock_request.get_json.return_value = json_data
    return mock_request


class VideoFrameRateParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_frame_rate(make_mock_request({'frameRate': 0}))
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_frame_rate(make_mock_request({'frameRate': 31
                                                              }))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            1,
            video_settings.parse_frame_rate(make_mock_request({'frameRate': 1
                                                              })))
        self.assertEqual(
            15,
            video_settings.parse_frame_rate(make_mock_request({'frameRate': 15
                                                              })))
        self.assertEqual(
            30,
            video_settings.parse_frame_rate(make_mock_request({'frameRate': 30
                                                              })))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoSettingError):
                    video_settings.parse_frame_rate(
                        make_mock_request({'frameRate': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_frame_rate(make_mock_request({'something': 1}))


class VideoMjpegQualityParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_mjpeg_quality(
                make_mock_request({'mjpegQuality': 0}))
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_mjpeg_quality(
                make_mock_request({'mjpegQuality': 101}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            1,
            video_settings.parse_mjpeg_quality(
                make_mock_request({'mjpegQuality': 1})))
        self.assertEqual(
            50,
            video_settings.parse_mjpeg_quality(
                make_mock_request({'mjpegQuality': 50})))
        self.assertEqual(
            100,
            video_settings.parse_mjpeg_quality(
                make_mock_request({'mjpegQuality': 100})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoSettingError):
                    video_settings.parse_mjpeg_quality(
                        make_mock_request({'mjpegQuality': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_mjpeg_quality(
                make_mock_request({'something': 1}))


class VideoH264BitrateParserTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 24}))
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 20001}))

    def test_accept_integers_within_bounds(self):
        self.assertEqual(
            25,
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 25})))
        self.assertEqual(
            5000,
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 5000})))
        self.assertEqual(
            20000,
            video_settings.parse_h264_bitrate(
                make_mock_request({'h264Bitrate': 20000})))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoSettingError):
                    video_settings.parse_h264_bitrate(
                        make_mock_request({'h264Bitrate': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_h264_bitrate(
                make_mock_request({'something': 1}))


class VideoStreamingModeParserTest(unittest.TestCase):

    def test_accept_valid_values(self):
        self.assertEqual(
            db.settings.StreamingMode.MJPEG,
            video_settings.parse_streaming_mode(
                make_mock_request({'streamingMode': 'MJPEG'})))
        self.assertEqual(
            db.settings.StreamingMode.H264,
            video_settings.parse_streaming_mode(
                make_mock_request({'streamingMode': 'H264'})))

    def test_reject_invalid_modes(self):
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_streaming_mode(
                make_mock_request({'streamingMode': 'mjpeg'}))
        with self.assertRaises(errors.InvalidVideoSettingError):
            video_settings.parse_streaming_mode(
                make_mock_request({'streamingMode': 'asdf'}))

    def test_reject_invalid_types(self):
        for value in [None, True, 15.0, (), [], {}]:
            with self.subTest(value):
                with self.assertRaises(errors.InvalidVideoSettingError):
                    video_settings.parse_streaming_mode(
                        make_mock_request({'streamingMode': value}))

    def test_reject_incorrect_key(self):
        with self.assertRaises(errors.MissingFieldError):
            video_settings.parse_streaming_mode(
                make_mock_request({'something': 'MJPEG'}))


class VideoH264StunParserTest(unittest.TestCase):

    def test_accept_valid_values(self):
        self.assertEqual(
            ('stun.example.com', 5672),
            video_settings.parse_stun_address(
                make_mock_request({'h264StunAddress': 'stun.example.com:5672'
                                  })))

        self.assertEqual(
            ('192.168.12.82', 15985),
            video_settings.parse_stun_address(
                make_mock_request({'h264StunAddress': '192.168.12.82:15985'})))

        self.assertEqual(
            ('0000:0000:0000:0000:0000:ffff:c0a8:0c52', 5672),
            video_settings.parse_stun_address(
                make_mock_request({
                    'h264StunAddress':
                        '[0000:0000:0000:0000:0000:ffff:c0a8:0c52]:5672'
                })))

        self.assertEqual(
            ('::ffff:c0a8:c52', 5672),
            video_settings.parse_stun_address(
                make_mock_request({'h264StunAddress': '[::ffff:c0a8:c52]:5672'
                                  })))
