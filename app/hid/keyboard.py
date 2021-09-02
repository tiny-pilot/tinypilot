from hid import write as hid_write


def send_keystroke(keyboard_path, control_keys, hid_keycode):
    buf = [0] * 8
    buf[0] = control_keys
    buf[2] = hid_keycode
    hid_write.write_to_hid_interface(keyboard_path, buf)

    # If it's a normal keycode (i.e. not a standalone modifier key), add a
    # message indicating that the key should be released after it is sent.
    if hid_keycode:
        release_keys(keyboard_path)


def release_keys(keyboard_path):
    hid_write.write_to_hid_interface(keyboard_path, [0] * 8)
