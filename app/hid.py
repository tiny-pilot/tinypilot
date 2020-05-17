_HID_DEVICE = '/dev/hidg0'

def send(hid_keycode):
  with open(_HID_DEVICE, 'rwb') as hid_handle:
    buf = [0] * 8
    buf[0] = hid_keycode
    hid_handle.write(buf)
