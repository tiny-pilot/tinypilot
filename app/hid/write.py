import logging
import multiprocessing

logger = logging.getLogger(__name__)

class Error(Exception):
    pass


class WriteError(Error):
    pass


def _write_to_hid_interface_immediately(hid_path, buffer):
    try:
        with open(hid_path, 'wb+') as hid_handle:
            hid_handle.write(bytearray(buffer))
    except BlockingIOError:
        logger.error('Failed to write to HID interface. Is USB cable connected?')


def write_to_hid_interface(hid_path, buffer):
    # Writes can hang, so attempt the write in a separate process to avoid
    # hanging.
    write_process = multiprocessing.Process(
        target=_write_to_hid_interface_immediately,
        args=(hid_path, buffer),
        daemon=True)
    write_process.start()
    write_process.join(timeout=0.5)
    # If the process is still alive, it means the write failed to complete in
    # time.
    if write_process.is_alive():
        write_process.kill()
        _wait_for_process_exit(write_process)
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for i in range(max_attempts):
        target_process.join(timeout=0.1)
