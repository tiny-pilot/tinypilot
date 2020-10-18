from hid import write as hid_write


def send_mouse_event(mouse_path, buttons, relative_x, relative_y, vwheel, hwheel):
    x, y = _scale_mouse_coordinates(relative_x, relative_y)

    buf = [0] * 7
    buf[0] = buttons
    buf[1] = x & 0xff
    buf[2] = (x >> 8) & 0xff
    buf[3] = y & 0xff
    buf[4] = (y >> 8) & 0xff
    buf[5] = _limit_scroll(vwheel) & 0xff
    buf[6] = _limit_scroll(hwheel) & 0xff
    hid_write.write_to_hid_interface(mouse_path, buf)


def _scale_mouse_coordinates(relative_x, relative_y):
    # This comes from LOGICAL_MAXIMUM in the mouse HID descriptor.
    max_hid_value = 32767.0
    x = int(relative_x * max_hid_value)
    y = int(relative_y * max_hid_value)
    return x, y


def _limit_scroll(wheel):
    return min(127, max(-127, wheel))
