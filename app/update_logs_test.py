import unittest

import update_logs


class UpdateLogsTest(unittest.TestCase):

    def test_get_new_logs_with_more_next_logs(self):
        self.assertEqual(
            "56789",
            update_logs.get_new_logs(prev_logs="01234", next_logs="0123456789"))

    def test_get_new_logs_with_more_prev_logs(self):
        self.assertEqual(
            "",
            update_logs.get_new_logs(prev_logs="0123456789", next_logs="01234"))

    def test_get_new_logs_with_no_common_logs(self):
        self.assertEqual(
            "56789",
            update_logs.get_new_logs(prev_logs="01234", next_logs="56789"))

    def test_get_new_logs_with_no_prev_logs(self):
        self.assertEqual(
            "0123456789",
            update_logs.get_new_logs(prev_logs="", next_logs="0123456789"))

    def test_get_new_logs_with_no_next_logs(self):
        self.assertEqual(
            "", update_logs.get_new_logs(prev_logs="01234", next_logs=""))
