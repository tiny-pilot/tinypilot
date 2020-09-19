class Error(Exception):
    pass


class WriteError(Error):
    pass


def write_to_hid_interface(hid_path, buffer):
    try:
        with open(hid_path, 'wb+') as hid_interface:
            hid_interface.write(bytearray(buffer))
    except BlockingIOError:
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')
