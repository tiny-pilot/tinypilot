import logging

from process import ProcessWithResult

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class WriteError(Error):
    pass


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
        logger.debug_sensitive('writing to HID interface %s: %s', hid_path,
                               ' '.join([f'{x:#04x}' for x in buffer]))
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
    if result is None or not result.was_successful():
        raise WriteError(f'Failed to write to HID interface: {hid_path}. '
                         'Is USB cable connected?')


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for _ in range(max_attempts):
        target_process.join(timeout=0.1)
