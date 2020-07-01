import threading


class Error(Exception):
    pass


class WriteError(Error):
    pass


def _write_to_hid_interface(hid_path, buffer):
    with open(hid_path, 'wb+') as hid_handle:
        hid_handle.write(bytearray(buffer))


def send(hid_path, control_keys, hid_keycode):
    # First 8 bytes are for the first keystorke. Second 8 bytes are
    # all zeroes to indicate completion of the keypress.
    buf = [0] * 16
    buf[0] = control_keys
    buf[2] = hid_keycode

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
