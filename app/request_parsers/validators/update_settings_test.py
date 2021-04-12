import unittest

from request_parsers.validators.update_settings import \
    _COMMON_DISPLAY_RESOLUTIONS
from request_parsers.validators.update_settings import validate_video_fps
from request_parsers.validators.update_settings import \
    validate_video_jpeg_quality
from request_parsers.validators.update_settings import \
    validate_video_resolution


class VideoResolutuinValidationTest(unittest.TestCase):

    def test_accept(self):
        for value in _COMMON_DISPLAY_RESOLUTIONS:
            with self.subTest(value):
                self.assertTrue(validate_video_resolution(value))

    def test_reject(self):
        valid_value = next(iter(_COMMON_DISPLAY_RESOLUTIONS))
        for value in [
                valid_value.upper(), f'{valid_value} ', f' {valid_value}', None,
                True, '', ' ', (), [], {}, 1
        ]:
            with self.subTest(value):
                self.assertFalse(validate_video_resolution(value))


class VideoFpsValidationTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        for value in [0, 31]:
            with self.subTest(value):
                self.assertFalse(validate_video_fps(value))

    def test_accept_integers_within_bounds(self):
        for value in range(1, 30 + 1):
            with self.subTest(value):
                self.assertTrue(validate_video_fps(value))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                self.assertFalse(validate_video_fps(value))


class VideoJpegQualityValidationTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        for value in [0, 101]:
            with self.subTest(value):
                self.assertFalse(validate_video_jpeg_quality(value))

    def test_accept_integers_within_bounds(self):
        for value in range(1, 100 + 1):
            with self.subTest(value):
                self.assertTrue(validate_video_jpeg_quality(value))

    def test_reject_non_integers(self):
        for value in [
                None, True, '', ' ', 'yes', '$', '3.0', '.1', 15.0, (), [], {}
        ]:
            with self.subTest(value):
                self.assertFalse(validate_video_jpeg_quality(value))
