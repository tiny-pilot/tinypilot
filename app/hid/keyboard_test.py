import tempfile
import unittest
from unittest import mock

from hid import keyboard
from hid import keycodes


class KeyboardTest(unittest.TestCase):

    @mock.patch.object(keyboard, 'release_keys')
    def test_send_hid_keycode_to_hid_interface(self, mock_release_keys):
        with tempfile.NamedTemporaryFile() as input_file:
            keyboard.send_keystroke(
                keyboard_path=input_file.name,
                control_keys=keycodes.KEYCODE_NONE,
                hid_keycode=keycodes.KEYCODE_A,
            )
            input_file.seek(0)
            self.assertEqual(b'\x00\x00\x04\x00\x00\x00\x00\x00',
                             input_file.read())
            mock_release_keys.assert_called_once()

    @mock.patch.object(keyboard, 'release_keys')
    def test_send_control_key_to_hid_interface(self, mock_release_keys):
        with tempfile.NamedTemporaryFile() as input_file:
            keyboard.send_keystroke(
                keyboard_path=input_file.name,
                control_keys=keycodes.MODIFIER_LEFT_SHIFT,
                hid_keycode=keycodes.KEYCODE_NONE,
            )
            input_file.seek(0)
            self.assertEqual(b'\x02\x00\x00\x00\x00\x00\x00\x00',
                             input_file.read())
            mock_release_keys.assert_not_called()

    @mock.patch.object(keyboard, 'release_keys')
    def test_send_control_key_and_hid_keycode_to_hid_interface(
            self, mock_release_keys):
        with tempfile.NamedTemporaryFile() as input_file:
            keyboard.send_keystroke(
                keyboard_path=input_file.name,
                control_keys=keycodes.MODIFIER_LEFT_SHIFT,
                hid_keycode=keycodes.KEYCODE_A,
            )
            input_file.seek(0)
            self.assertEqual(b'\x02\x00\x04\x00\x00\x00\x00\x00',
                             input_file.read())
            mock_release_keys.assert_called_once()

    def test_send_release_keys_to_hid_interface(self):
        with tempfile.NamedTemporaryFile() as input_file:
            keyboard.release_keys(keyboard_path=input_file.name)
            self.assertEqual(b'\x00\x00\x00\x00\x00\x00\x00\x00',
                             input_file.read())
