import unittest

from app import dummy


class DummyTest(unittest.TestCase):
    """Replace this with a real unit test class."""

    def test_dummy(self):
        self.assertEqual('dummy', dummy.dummy())
