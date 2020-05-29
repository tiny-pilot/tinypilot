def send(hid_path, control_keys, hid_keycode):
    with open(hid_path, 'wb+') as hid_handle:
        buf = [0] * 8
        buf[0] = control_keys
        buf[2] = hid_keycode
        hid_handle.write(bytearray(buf))
        hid_handle.write(bytearray([0] * 8))
