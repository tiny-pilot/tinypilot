import unittest

from request_parsers.validators import video_fps


class VideoFpsValidationTest(unittest.TestCase):

    def test_reject_integers_out_of_bounds(self):
        self.assertFalse(video_fps.validate(0))
        self.assertFalse(video_fps.validate(31))

    def test_accept_integers_within_bounds(self):
        self.assertTrue(video_fps.validate(1))
        self.assertTrue(video_fps.validate(15))
        self.assertTrue(video_fps.validate(30))
