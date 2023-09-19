from hid import write as hid_write


def send_keystroke(keyboard_path, keystroke):
    buf = [0] * 8
    buf[0] = keystroke.modifier
    buf[2] = keystroke.keycode
    hid_write.write_to_hid_interface(keyboard_path, buf)

    # If it's a normal keycode (i.e. not a standalone modifier key), add a
    # message indicating that the key should be released after it is sent. We do
    # this to prevent the keystroke from incorrectly repeating on the target
    # machine if network latency causes a delay between the keydown and keyup
    # events. However, auto-releasing has the disadvantage of preventing
    # genuinely long key presses (see
    # https://github.com/tiny-pilot/tinypilot/issues/1093).
    if keystroke.keycode:
        release_keys(keyboard_path)


def release_keys(keyboard_path):
    hid_write.write_to_hid_interface(keyboard_path, [0] * 8)


def send_keystrokes(keyboard_path, keystrokes):
    """Sends multiple keystrokes to the HID interface, one after the other.

    Args:
        keyboard_path: The file path to the keyboard interface.
        keystrokes: A list of HID Keystroke objects.

    Raises:
        WriteError: If a keystroke fails to be written to the HID interface.
    """
    for keystroke in keystrokes:
        send_keystroke(keyboard_path, keystroke.modifier, keystroke.keycode)
