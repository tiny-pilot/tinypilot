from hid import write as hid_write

RELEASE_KEYS_BUFFER = bytes([0] * 8)


def keystroke_to_buffer(control_keys, hid_keycode):
    buf = bytearray(RELEASE_KEYS_BUFFER)
    buf[0] = control_keys
    buf[2] = hid_keycode

    # If it's a normal keycode (i.e. not a standalone modifier key), add a
    # message indicating that the key should be released after it is sent. We do
    # this to prevent the keystroke from incorrectly repeating on the target
    # machine if network latency causes a delay between the keydown and keyup
    # events. However, auto-releasing has the disadvantage of preventing
    # genuinely long key presses (see
    # https://github.com/tiny-pilot/tinypilot/issues/1093).
    if hid_keycode:
        buf += RELEASE_KEYS_BUFFER

    return buf


def send_keystroke(keyboard_path, control_keys, hid_keycode):
    buf = keystroke_to_buffer(control_keys, hid_keycode)
    hid_write.write_to_hid_interface(keyboard_path, buf)


def release_keys(keyboard_path):
    hid_write.write_to_hid_interface(keyboard_path, RELEASE_KEYS_BUFFER)
