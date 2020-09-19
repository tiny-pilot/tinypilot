import os


class Error(Exception):
    pass


class WriteError(Error):
    pass


def write_to_hid_interface(hid_path, buffer):
    hid_fd = 0
    try:
        # Open the HID interface in non-blocking mode. Otherwise, if the write
        # fails, for example due to a cable that's incompatible or broken, the
        # write will hang indefinitely, locking up the process.
        hid_fd = os.open(hid_path, os.O_RDWR | os.O_NONBLOCK)
        os.write(hid_fd, bytearray(buffer))
    except BlockingIOError:
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')
    finally:
        if hid_fd:
            os.close(hid_fd)
