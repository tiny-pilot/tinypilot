import tempfile
import unittest

from app.hid import mouse


class MouseTest(unittest.TestCase):

    def test_sends_mouse_click_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            mouse.send_mouse_event(mouse_path=input_file.name,
                                   buttons=0x01,
                                   relative_x=0.5,
                                   relative_y=0.75,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=0),
            input_file.seek(0)
            # Byte 0   = Button 1 pressed
            # Byte 1-2 = 32767 * 0.5 = 16383.5 = 0x3fff (little-endian)
            # Byte 3-4 = 32767 * 0.75 = 24575.25 = 0x5fff (little-endian)
            self.assertEqual(b'\x01\xff\x3f\xff\x5f\x00\x00', input_file.read())

    def test_sends_mouse_move_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            mouse.send_mouse_event(mouse_path=input_file.name,
                                   buttons=0,
                                   relative_x=0.0,
                                   relative_y=1.0,
                                   vertical_wheel_delta=0,
                                   horizontal_wheel_delta=0),
            input_file.seek(0)
            # Byte 0   = No buttons pressed
            # Byte 1-2 = 32767 * 0.0 = 0 = 0x0000
            # Byte 3-4 = 32767 * 1.0 = 32767 = 0x7fff (little-endian)
            self.assertEqual(b'\x00\x00\x00\xff\x7f\x00\x00', input_file.read())
