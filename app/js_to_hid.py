import dataclasses


class Error(Exception):
    pass


class UnrecognizedKeyCodeError(Error):
    pass


@dataclasses.dataclass
class JavaScriptKeyEvent:
    right_meta_modifier: bool
    right_alt_modifier: bool
    right_shift_modifier: bool
    right_ctrl_modifier: bool
    left_meta_modifier: bool
    left_alt_modifier: bool
    left_shift_modifier: bool
    left_ctrl_modifier: bool
    key: str
    key_code: int


# JS keycodes source: https://github.com/wesbos/keycodes
# HID keycodes source: https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

# TODO: For simplicity, we map all modifiers keys to the left key, but we could
# support distinct keys for left and right if we check the location parameter
# from the JavaScript message.
_JS_TO_HID_KEYCODES = {
    3: 0x48,  # Pause / Break
    8: 0x2a,  # Backspace / Delete
    9: 0x2b,  # Tab
    12: 0x53,  # Clear
    13: 0x28,  # Enter
    16: 0xe1,  # Shift (Left)
    17: 0xe0,  # Ctrl (left)
    18: 0xe1,  # Alt (left)
    19: 0x48,  # Pause / Break
    20: 0x39,  # Caps Lock
    21: 0x90,  # Hangeul
    25: 0x91,  # Hanja
    27: 0x29,  # Escape
    32: 0x2c,  # Spacebar
    33: 0x4b,  # Page Up
    34: 0x4e,  # Page Down
    35: 0x4d,  # End
    36: 0x4a,  # Home
    37: 0x50,  # Left Arrow
    38: 0x52,  # Up Arrow
    39: 0x4f,  # Right Arrow
    40: 0x51,  # Down Arrow
    41: 0x77,  # Select
    43: 0x74,  # Execute
    44: 0x46,  # Print Screen
    45: 0x49,  # Insert
    46: 0x4c,  # Delete
    47: 0x75,  # Help
    48: 0x27,  # 0
    49: 0x1e,  # 1
    50: 0x1f,  # 2
    51: 0x20,  # 3
    52: 0x21,  # 4
    53: 0x22,  # 5
    54: 0x23,  # 6
    55: 0x24,  # 7
    56: 0x25,  # 8
    57: 0x26,  # 9
    59: 0x33,  # Semicolon
    60: 0xc5,  # <
    61: 0x2e,  # Equal sign
    65: 0x04,  # a
    66: 0x05,  # b
    67: 0x06,  # c
    68: 0x07,  # d
    69: 0x08,  # e
    70: 0x09,  # f
    71: 0x0a,  # g
    72: 0x0b,  # h
    73: 0x0c,  # i
    74: 0x0d,  # j
    75: 0x0e,  # k
    76: 0x0f,  # l
    77: 0x10,  # m
    78: 0x11,  # n
    79: 0x12,  # o
    80: 0x13,  # p
    81: 0x14,  # q
    82: 0x15,  # r
    83: 0x16,  # s
    84: 0x17,  # t
    85: 0x18,  # u
    86: 0x19,  # v
    87: 0x1a,  # w
    88: 0x1b,  # x
    89: 0x1c,  # y
    90: 0x1d,  # z
    91: 0xe3,  # Windows key / Meta Key (Left)
    96: 0x62,  # Numpad 0
    97: 0x59,  # Numpad 1
    98: 0x5a,  # Numpad 2
    99: 0x5b,  # Numpad 3
    100: 0x5c,  # Numpad 4
    101: 0x5d,  # Numpad 5
    102: 0x5e,  # Numpad 6
    103: 0x5f,  # Numpad 7
    104: 0x60,  # Numpad 8
    105: 0x61,  # Numpad 9
    112: 0x3b,  # F1
    113: 0x3c,  # F2
    114: 0x3d,  # F3
    115: 0x3e,  # F4
    116: 0x3f,  # F5
    117: 0x40,  # F6
    118: 0x41,  # F7
    119: 0x42,  # F8
    120: 0x43,  # F9
    121: 0x44,  # F10
    122: 0x45,  # F11
    123: 0x46,  # F12
    124: 0x68,  # F13
    125: 0x69,  # F14
    126: 0x6a,  # F15
    127: 0x6b,  # F16
    128: 0x6c,  # F17
    129: 0x6d,  # F18
    130: 0x6e,  # F19
    131: 0x6f,  # F20
    132: 0x70,  # F21
    133: 0x71,  # F22
    134: 0x72,  # F23
    144: 0x53,  # Num Lock
    145: 0x47,  # Scroll Lock
    161: 0x1e,  # !
    163: 0x32,  # Hash
    173: 0x2d,  # Minus
    179: 0xe8,  # Media play/pause
    168: 0xfa,  # Refresh
    186: 0x33,  # Semicolon
    187: 0x2e,  # Equal sign
    188: 0x36,  # Comma
    189: 0x2d,  # Minus sign
    190: 0x37,  # Period
    191: 0x38,  # Forward slash
    192: 0x35,  # Accent grave
    219: 0x2f,  # Left bracket ([, {])
    220: 0x31,  # Back slash
    221: 0x30,  # Right bracket (], })
    222: 0x34,  # Single quote
    223: 0x35,  # Accent grave (`)
}


def convert(js_key_event):
    control_chars = 0
    for i, pressed in enumerate([
            js_key_event.left_ctrl_modifier, js_key_event.left_shift_modifier,
            js_key_event.left_alt_modifier, js_key_event.left_meta_modifier,
            js_key_event.right_ctrl_modifier, js_key_event.right_shift_modifier,
            js_key_event.right_alt_modifier, js_key_event.right_meta_modifier
    ]):
        if pressed:
            control_chars |= 1 << i
    try:
        return control_chars, _JS_TO_HID_KEYCODES[js_key_event.key_code]
    except KeyError:
        raise UnrecognizedKeyCodeError(
            'Unrecognized key code %s (%d)' %
            (js_key_event.key, js_key_event.key_code))
