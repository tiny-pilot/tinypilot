from hid import keycodes as hid
from hid import write as hid_write

_MODIFIER_KEYCODES = [
    hid.KEYCODE_LEFT_CTRL, hid.KEYCODE_LEFT_SHIFT, hid.KEYCODE_LEFT_ALT,
    hid.KEYCODE_LEFT_META, hid.KEYCODE_RIGHT_CTRL, hid.KEYCODE_RIGHT_SHIFT,
    hid.KEYCODE_RIGHT_ALT, hid.KEYCODE_RIGHT_META
]


def send_keystroke(keyboard_path, control_keys, hid_keycode):
    # First 8 bytes are for the first keystroke. Second 8 bytes are
    # all zeroes to indicate release of keys.
    buf = [0] * 8
    buf[0] = control_keys
    buf[2] = hid_keycode
    hid_write.write_to_hid_interface(keyboard_path, buf)

    # If it's not a modifier keycode, add a message indicating that the key
    # should be released after it is sent.
    if hid_keycode not in _MODIFIER_KEYCODES:
        release_keys(keyboard_path)


def release_keys(keyboard_path):
    hid_write.write_to_hid_interface(keyboard_path, [0] * 8)
