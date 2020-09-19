import os


class Error(Exception):
    pass


class WriteError(Error):
    pass


def write_to_hid_interface(hid_path, buffer):
    hid_fd = 0
    try:
        hid_fd = os.open(hid_path, os.O_RDWR)
        os.write(hid_fd, bytearray(buffer))
    except BlockingIOError:
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')
    finally:
        if hid_fd:
            os.close(hid_fd)
