import threading


class Error(Exception):
    pass


class WriteError(Error):
    pass


def _write_to_hid_interface_immediately(hid_path, buffer):
    with open(hid_path, 'wb+') as hid_handle:
        hid_handle.write(bytearray(buffer))


def write_to_hid_interface(hid_path, buffer):
    # Writes can time out, so attempt the write in a separate thread to avoid
    # hanging.
    write_thread = threading.Thread(target=_write_to_hid_interface_immediately,
                                    args=(hid_path, buffer))
    write_thread.start()
    write_thread.join(timeout=0.5)
    if write_thread.is_alive():
        # If the thread is still alive, it means the join timed out.
        raise WriteError(
            'Failed to write to HID interface. Is USB cable connected?')