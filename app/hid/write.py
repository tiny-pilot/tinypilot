import logging
import multiprocessing

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class WriteError(Error):
    pass


class ProcessWithResult(multiprocessing.Process):
    """A multiprocessing.Process object that keeps track of the child process'
    result (i.e., the return value and exception raised).

    Inspired by:
    https://stackoverflow.com/a/33599967/3769045
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the Connection objects used for communication between the
        # parent and child processes.
        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self):
        """Method to be run in sub-process."""
        result = {'return_value': None, 'exception': None}
        try:
            if self._target:
                result['return_value'] = self._target(*self._args,
                                                      **self._kwargs)
        except Exception as e:
            result['exception'] = e
            raise
        finally:
            self.child_conn.send(result)

    def result(self):
        """Get the result from the child process.

        Returns:
            If the child process has completed, a dictionay with the following
            keys are returned:
            return_value: Any object. If no object was returned, this will be
                None.
            exception: Exception object. If no exception was raised, then this
                will be None.

            Example:
            {
                'return_value': None,
                'exception': WriteError('Failed to write to HID interface')
            }

            If the child process has not yet completed, returns None.
        """
        return self.parent_conn.recv() if self.parent_conn.poll() else None


def _write_to_hid_interface_immediately(hid_path, buffer):
    try:
        with open(hid_path, 'ab+') as hid_handle:
            hid_handle.write(bytearray(buffer))
    except BlockingIOError:
        logger.error(
            'Failed to write to HID interface: %s. Is USB cable connected?',
            hid_path)


def write_to_hid_interface(hid_path, buffer):
    # Avoid an unnecessary string formatting call in a write that requires low
    # latency.
    if logger.getEffectiveLevel() == logging.DEBUG:
        logger.debug('writing to HID interface %s: %s', hid_path,
                     ' '.join(['0x%02x' % x for x in buffer]))
    # Writes can hang, for example, when TinyPilot is attempting to write to the
    # mouse interface, but the target system has no GUI. To avoid locking up the
    # main server process, perform the HID interface I/O in a separate process.
    write_process = ProcessWithResult(
        target=_write_to_hid_interface_immediately,
        args=(hid_path, buffer),
        daemon=True)
    write_process.start()
    write_process.join(timeout=0.5)
    if write_process.is_alive():
        write_process.kill()
        _wait_for_process_exit(write_process)
    result = write_process.result()
    # If the result is None, it means the write failed to complete in time.
    if result is None or result['exception']:
        raise WriteError(
            'Failed to write to HID interface: %s. Is USB cable connected?' %
            hid_path)


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for _ in range(max_attempts):
        target_process.join(timeout=0.1)
