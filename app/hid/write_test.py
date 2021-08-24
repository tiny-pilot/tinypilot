import io
import time
import unittest
from unittest import mock

import hid.write


class WriteTest(unittest.TestCase):

    def test_process_with_result_child_completed(self):

        def target():
            pass

        process = hid.write.ProcessWithResult(target=target, daemon=True)
        process.start()
        process.join()
        self.assertEqual({
            'return_value': None,
            'exception': None
        }, process.result())

    def test_process_with_result_child_not_completed(self):

        def target():
            time.sleep(1)

        process = hid.write.ProcessWithResult(target=target, daemon=True)
        process.start()
        process.kill()
        self.assertIsNone(process.result())

    def test_process_with_result_child_exception(self):

        def target():
            raise Exception('Child exception')

        # Silence stderr while the child exception is being raised to avoid
        # polluting the terminal output.
        with mock.patch('sys.stderr', io.StringIO()):
            process = hid.write.ProcessWithResult(target=target, daemon=True)
            process.start()
            process.join()
        result = process.result()
        self.assertEqual({'return_value': None, 'exception': mock.ANY}, result)
        self.assertEqual('Child exception', str(result['exception']))
