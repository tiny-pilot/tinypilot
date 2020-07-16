import threading


class Error(Exception):
    pass


class WriteError(Error):
    pass


KEYCODE_LEFT_CTRL = 0xe0
KEYCODE_LEFT_SHIFT = 0xe1
KEYCODE_LEFT_ALT = 0xe2
KEYCODE_LEFT_META = 0xe3
_MODIFIER_KEYCODES = [
    KEYCODE_LEFT_CTRL, KEYCODE_LEFT_SHIFT, KEYCODE_LEFT_ALT, KEYCODE_LEFT_META
]


def _write_to_hid_interface(hid_path, buffer):
    with open(hid_path, 'wb+') as hid_handle:
        hid_handle.write(bytearray(buffer))


def send(hid_path, control_keys, hid_keycode):
    # First 8 bytes are for the first keystorke. Second 8 bytes are
    # all zeroes to indicate release of keys.
    buf = [0] * 8
    buf[0] = control_keys
    buf[2] = hid_keycode

    # If it's not a modifier keycode, add a message indicating that the key
    # should be released after it is sent.
    if hid_keycode not in _MODIFIER_KEYCODES:
        buf += [0] * 8

    # Writes can time out, so attempt the write in a separate thread to avoid
    # hanging.
    write_thread = threading.Thread(target=_write_to_hid_interface,
                                    args=(hid_path, buf))
    write_thread.start()
    write_thread.join(timeout=0.5)
    if write_thread.is_alive():
        # If the thread is still alive, it means the join timed out.
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')
