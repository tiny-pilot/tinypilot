import io
import time
import unittest
from unittest import mock

import hid.write

# Dummy functions to represent what can happen when a Human Interface Device
# writes.
#
# On some MacOS systems, the multiprocessing module spawns rather than forks new
# processes[1], which pickles these functions[2]. So, they must be defined
# using `def` at the top level of a module[3].
#
# This was observed on a 2021 Macbook Pro M1 Max running OSX Ventura 13.2.1.
#
# [1] https://github.com/python/cpython/commit/17a5588740b3d126d546ad1a13bdac4e028e6d50
# [2] https://docs.python.org/3.9/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
# [3] https://docs.python.org/3.9/library/pickle.html#what-can-be-pickled-and-unpickled:~:text=(using%20def%2C%20not%20lambda)


def do_nothing():
    pass


def sleep_1_second():
    time.sleep(1)


def raise_exception():
    raise Exception('Child exception')


def return_string():
    return 'Done!'


class WriteTest(unittest.TestCase):

    def test_process_with_result_child_completed(self):
        process = hid.write.ProcessWithResult(target=do_nothing, daemon=True)
        process.start()
        process.join()
        result = process.result()
        self.assertTrue(result.was_successful())
        self.assertEqual(
            hid.write.ProcessResult(return_value=None, exception=None), result)

    def test_process_with_result_child_not_completed(self):
        process = hid.write.ProcessWithResult(target=sleep_1_second,
                                              daemon=True)
        process.start()
        # Get the result before the child process has completed.
        self.assertIsNone(process.result())

        # Clean up the running child process.
        process.kill()

    def test_process_with_result_child_exception(self):
        # Silence stderr while the child exception is being raised to avoid
        # polluting the terminal output.
        with mock.patch('sys.stderr', io.StringIO()):
            process = hid.write.ProcessWithResult(target=raise_exception,
                                                  daemon=True)
            process.start()
            process.join()
        result = process.result()
        self.assertFalse(result.was_successful())
        self.assertEqual(
            hid.write.ProcessResult(return_value=None, exception=mock.ANY),
            result)
        self.assertEqual('Child exception', str(result.exception))

    def test_process_with_result_return_value(self):
        process = hid.write.ProcessWithResult(target=return_string, daemon=True)
        process.start()
        process.join()
        result = process.result()
        self.assertTrue(result.was_successful())
        self.assertEqual(
            hid.write.ProcessResult(return_value='Done!', exception=None),
            result)
