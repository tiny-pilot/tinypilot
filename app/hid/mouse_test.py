import tempfile
import unittest

from hid import mouse as fake_mouse


class MouseTest(unittest.TestCase):

    def test_sends_mouse_click_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0x01,
                                        relative_x=0.5,
                                        relative_y=0.75,
                                        vertical_wheel_delta=0,
                                        horizontal_wheel_delta=0)
            input_file.seek(0)
            # Byte 0   = Button 1 pressed
            # Byte 1-2 = 32767 * 0.5 = 16383.5 = 0x3fff (little-endian)
            # Byte 3-4 = 32767 * 0.75 = 24575.25 = 0x5fff (little-endian)
            self.assertEqual(b'\x01\xff\x3f\xff\x5f\x00\x00', input_file.read())

    def test_sends_mouse_move_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0,
                                        relative_x=0.0,
                                        relative_y=1.0,
                                        vertical_wheel_delta=0,
                                        horizontal_wheel_delta=0)
            input_file.seek(0)
            # Byte 0   = No buttons pressed
            # Byte 1-2 = 32767 * 0.0 = 0 = 0x0000
            # Byte 3-4 = 32767 * 1.0 = 32767 = 0x7fff (little-endian)
            self.assertEqual(b'\x00\x00\x00\xff\x7f\x00\x00', input_file.read())

    def test_sends_scroll_down_and_right_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0,
                                        relative_x=0.0,
                                        relative_y=0.0,
                                        vertical_wheel_delta=1,
                                        horizontal_wheel_delta=1)
            input_file.seek(0)
            # Byte 5 = Vertical wheel: JS scroll down (1) is HID -1 (0xff)
            # Byte 6 = Horizontal wheel: JS scroll right (1) is HID 1 (0x01)
            self.assertEqual(b'\x00\x00\x00\x00\x00\xff\x01', input_file.read())

    def test_sends_scroll_up_and_left_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0,
                                        relative_x=0.0,
                                        relative_y=0.0,
                                        vertical_wheel_delta=-1,
                                        horizontal_wheel_delta=-1)
            input_file.seek(0)
            # Byte 5 = Vertical wheel: JS scroll up (-1) is HID 1 (0x01)
            # Byte 6 = Horizontal wheel: JS scroll left (-1) is HID -1 (0xff)
            self.assertEqual(b'\x00\x00\x00\x00\x00\x01\xff', input_file.read())

    def test_inverts_scroll_direction_on_both_axes(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0,
                                        relative_x=0.0,
                                        relative_y=0.0,
                                        vertical_wheel_delta=1,
                                        horizontal_wheel_delta=1,
                                        invert_scroll_direction=True)
            input_file.seek(0)
            # Byte 5 = Vertical wheel: JS scroll down (1), inverted to scroll
            #          up, is HID 1 (0x01)
            # Byte 6 = Horizontal wheel: JS scroll right (1), inverted to
            #          scroll left, is HID -1 (0xff)
            self.assertEqual(b'\x00\x00\x00\x00\x00\x01\xff', input_file.read())

    def test_inverting_scroll_direction_does_not_affect_other_fields(self):
        with tempfile.NamedTemporaryFile() as input_file:
            fake_mouse.send_mouse_event(mouse_path=input_file.name,
                                        buttons=0x01,
                                        relative_x=0.5,
                                        relative_y=0.75,
                                        vertical_wheel_delta=0,
                                        horizontal_wheel_delta=0,
                                        invert_scroll_direction=True)
            input_file.seek(0)
            # Same as the plain click test: buttons and coordinates are
            # unchanged, and a zero wheel delta stays zero.
            self.assertEqual(b'\x01\xff\x3f\xff\x5f\x00\x00', input_file.read())
