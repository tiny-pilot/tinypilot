import unittest

from request_parsers.validators import video_jpeg_quality


class VideoJpegQualityValidationTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        self.assertFalse(video_jpeg_quality.validate(0))
        self.assertFalse(video_jpeg_quality.validate(101))

    def test_accept_integers_within_bounds(self):
        self.assertTrue(video_jpeg_quality.validate(1))
        self.assertTrue(video_jpeg_quality.validate(50))
        self.assertTrue(video_jpeg_quality.validate(100))
