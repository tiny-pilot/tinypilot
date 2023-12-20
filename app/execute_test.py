import contextlib
import io
import time
import unittest
from unittest import mock

import execute

# Dummy functions to represent what can happen when a Human Interface Device
# writes.
#
# On some MacOS systems, the multiprocessing module spawns rather than forks new
# processes[1], which pickles these functions[2]. So, they must be defined
# using `def` at the top level of a module[3].
#
# Another by-effect of this is that the `silence_stderr` context manager
# doesn’t have any effect on MacOS systems, so we cannot prevent the stacktrace
# printing there.[4]
#
# This was observed on a 2021 Macbook Pro M1 Max running OSX Ventura 13.2.1.
#
# [1] https://github.com/python/cpython/commit/17a5588740b3d126d546ad1a13bdac4e028e6d50
# [2] https://docs.python.org/3.9/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
# [3] https://docs.python.org/3.9/library/pickle.html#what-can-be-pickled-and-unpickled:~:text=(using%20def%2C%20not%20lambda)
# [4] https://github.com/tiny-pilot/tinypilot/issues/1713


def do_nothing():
    pass


def sleep_1_second():
    time.sleep(1)


def raise_exception():
    raise Exception('Child exception')


def return_string():
    return 'Done!'


@contextlib.contextmanager
def silence_stderr():
    """Silences stderr to avoid polluting the terminal output of the tests."""
    # Note: on MacOS systems, this doesn’t have an effect (see comment above).
    with mock.patch('sys.stderr', io.StringIO()):
        yield None


class ExecuteTest(unittest.TestCase):

    def test_process_with_result_child_completed(self):
        process = execute.ProcessWithResult(target=do_nothing, daemon=True)
        process.start()
        process.join()
        result = process.result()
        self.assertTrue(result.was_successful())
        self.assertEqual(
            execute.ProcessResult(return_value=None, exception=None), result)

    def test_process_with_result_child_not_completed(self):
        process = execute.ProcessWithResult(target=sleep_1_second, daemon=True)
        process.start()
        # Get the result before the child process has completed.
        self.assertIsNone(process.result())

        # Clean up the running child process.
        process.kill()

    def test_process_with_result_child_exception(self):
        # Silence stderr while the child exception is being raised to avoid
        # polluting the terminal output.
        with silence_stderr():
            process = execute.ProcessWithResult(target=raise_exception,
                                                daemon=True)
            process.start()
            process.join()
        result = process.result()
        self.assertFalse(result.was_successful())
        self.assertEqual(
            execute.ProcessResult(return_value=None, exception=mock.ANY),
            result)
        self.assertEqual('Child exception', str(result.exception))

    def test_process_with_result_return_value(self):
        process = execute.ProcessWithResult(target=return_string, daemon=True)
        process.start()
        process.join()
        result = process.result()
        self.assertTrue(result.was_successful())
        self.assertEqual(
            execute.ProcessResult(return_value='Done!', exception=None), result)

    def test_execute_with_timeout_and_timeout_reached(self):
        with self.assertRaises(TimeoutError):
            execute.with_timeout(sleep_1_second, timeout_in_seconds=0.5)

    def test_execute_with_timeout_return_value(self):
        return_value = execute.with_timeout(return_string,
                                            timeout_in_seconds=0.5)
        self.assertEqual('Done!', return_value)

    def test_execute_with_timeout_child_exception(self):
        with silence_stderr():
            with self.assertRaises(Exception) as ctx:
                execute.with_timeout(raise_exception, timeout_in_seconds=0.5)
        self.assertEqual('Child exception', str(ctx.exception))

    def test_background_thread_ignores_function_successful(self):
        self.assertEqual(None, execute.background_thread(return_string))

    def test_background_thread_ignores_function_exception(self):
        with silence_stderr():
            self.assertEqual(None, execute.background_thread(raise_exception))
