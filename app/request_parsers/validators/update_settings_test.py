import unittest

from request_parsers.validators.update_settings import validate_video_fps


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
