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
            'Failed to write to HID interface: %s. Is USB cable connected?' %
            hid_path)


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for i in range(max_attempts):
        target_process.join(timeout=0.1)
