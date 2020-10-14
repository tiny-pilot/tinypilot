from hid.keycodes import azerty
from hid.keycodes import modifiers
from hid.keycodes import qwerty


class Error(Exception):
    pass


class UnrecognizedKeyCodeError(Error):
    pass


class InvalidKeyboardLayout(Error):
    pass


def convert(keystroke, keyboard_layout_string):
    keycode_mapping = _get_keycode_mapping(keyboard_layout_string,
                                           keystroke.is_right_modifier)
    try:
        return _map_modifier_keys(keystroke), keycode_mapping[
            keystroke.key_code]
    except KeyError:
        raise UnrecognizedKeyCodeError('Unrecognized key code %s (%d)' %
                                       (keystroke.key, keystroke.key_code))


def _get_keycode_mapping(keyboard_layout_string, is_right_modifier):
    layout = _get_target_keyboard_layout(keyboard_layout_string)

    # Use a shorter variable name to avoid screwing up the nice dict format
    # below.
    right = is_right_modifier

    # JS keycodes source: https://github.com/wesbos/keycodes
    return {
        3: layout.KEYCODE_PAUSE_BREAK,
        8: layout.KEYCODE_BACKSPACE_DELETE,
        9: layout.KEYCODE_TAB,
        12: layout.KEYCODE_CLEAR,
        13: layout.KEYCODE_ENTER,
        16: layout.KEYCODE_RIGHT_SHIFT if right else layout.KEYCODE_LEFT_SHIFT,
        17: layout.KEYCODE_RIGHT_CTRL if right else layout.KEYCODE_LEFT_CTRL,
        18: layout.KEYCODE_RIGHT_ALT if right else layout.KEYCODE_LEFT_ALT,
        19: layout.KEYCODE_PAUSE_BREAK,
        20: layout.KEYCODE_CAPS_LOCK,
        21: layout.KEYCODE_HANGEUL,
        25: layout.KEYCODE_HANJA,
        27: layout.KEYCODE_ESCAPE,
        32: layout.KEYCODE_SPACEBAR,
        33: layout.KEYCODE_PAGE_UP,
        34: layout.KEYCODE_PAGE_DOWN,
        35: layout.KEYCODE_END,
        36: layout.KEYCODE_HOME,
        37: layout.KEYCODE_LEFT_ARROW,
        38: layout.KEYCODE_UP_ARROW,
        39: layout.KEYCODE_RIGHT_ARROW,
        40: layout.KEYCODE_DOWN_ARROW,
        41: layout.KEYCODE_SELECT,
        43: layout.KEYCODE_EXECUTE,
        44: layout.KEYCODE_PRINT_SCREEN,
        45: layout.KEYCODE_INSERT,
        46: layout.KEYCODE_DELETE,
        47: layout.KEYCODE_HELP,
        48: layout.KEYCODE_NUMBER_0,
        49: layout.KEYCODE_NUMBER_1,
        50: layout.KEYCODE_NUMBER_2,
        51: layout.KEYCODE_NUMBER_3,
        52: layout.KEYCODE_NUMBER_4,
        53: layout.KEYCODE_NUMBER_5,
        54: layout.KEYCODE_NUMBER_6,
        55: layout.KEYCODE_NUMBER_7,
        56: layout.KEYCODE_NUMBER_8,
        57: layout.KEYCODE_NUMBER_9,
        58: layout.KEYCODE_COLON,
        59: layout.KEYCODE_SEMICOLON,
        60: layout.KEYCODE_LESS_THAN,
        61: layout.KEYCODE_EQUAL_SIGN,
        65: layout.KEYCODE_A,
        66: layout.KEYCODE_B,
        67: layout.KEYCODE_C,
        68: layout.KEYCODE_D,
        69: layout.KEYCODE_E,
        70: layout.KEYCODE_F,
        71: layout.KEYCODE_G,
        72: layout.KEYCODE_H,
        73: layout.KEYCODE_I,
        74: layout.KEYCODE_J,
        75: layout.KEYCODE_K,
        76: layout.KEYCODE_L,
        77: layout.KEYCODE_M,
        78: layout.KEYCODE_N,
        79: layout.KEYCODE_O,
        80: layout.KEYCODE_P,
        81: layout.KEYCODE_Q,
        82: layout.KEYCODE_R,
        83: layout.KEYCODE_S,
        84: layout.KEYCODE_T,
        85: layout.KEYCODE_U,
        86: layout.KEYCODE_V,
        87: layout.KEYCODE_W,
        88: layout.KEYCODE_X,
        89: layout.KEYCODE_Y,
        90: layout.KEYCODE_Z,
        91: layout.KEYCODE_RIGHT_META if right else layout.KEYCODE_LEFT_META,
        93: layout.KEYCODE_CONTEXT_MENU,
        94: layout.KEYCODE_NUMPAD_4,  # / (UK)
        96: layout.KEYCODE_NUMPAD_0,
        97: layout.KEYCODE_NUMPAD_1,
        98: layout.KEYCODE_NUMPAD_2,
        99: layout.KEYCODE_NUMPAD_3,
        100: layout.KEYCODE_NUMPAD_4,
        101: layout.KEYCODE_NUMPAD_5,
        102: layout.KEYCODE_NUMPAD_6,
        103: layout.KEYCODE_NUMPAD_7,
        104: layout.KEYCODE_NUMPAD_8,
        105: layout.KEYCODE_NUMPAD_9,
        106: layout.KEYCODE_NUMPAD_MULTIPLY,
        107: layout.KEYCODE_NUMPAD_PLUS,
        109: layout.KEYCODE_NUMPAD_MINUS,
        110: layout.KEYCODE_NUMPAD_DOT,
        111: layout.KEYCODE_NUMPAD_DIVIDE,
        112: layout.KEYCODE_F1,
        113: layout.KEYCODE_F2,
        114: layout.KEYCODE_F3,
        115: layout.KEYCODE_F4,
        116: layout.KEYCODE_F5,
        117: layout.KEYCODE_F6,
        118: layout.KEYCODE_F7,
        119: layout.KEYCODE_F8,
        120: layout.KEYCODE_F9,
        121: layout.KEYCODE_F10,
        122: layout.KEYCODE_F11,
        123: layout.KEYCODE_F12,
        124: layout.KEYCODE_F13,
        125: layout.KEYCODE_F14,
        126: layout.KEYCODE_F15,
        127: layout.KEYCODE_F16,
        128: layout.KEYCODE_F17,
        129: layout.KEYCODE_F18,
        130: layout.KEYCODE_F19,
        131: layout.KEYCODE_F20,
        132: layout.KEYCODE_F21,
        133: layout.KEYCODE_F22,
        134: layout.KEYCODE_F23,
        144: layout.KEYCODE_NUM_LOCK,
        145: layout.KEYCODE_SCROLL_LOCK,
        161: layout.KEYCODE_LESS_THAN,
        163: layout.KEYCODE_HASH,
        164: layout.KEYCODE_DOLLAR_SIGN,
        165: layout.KEYCODE_U_ACCENT,
        169: layout.KEYCODE_RIGHT_PARENTHESIS,
        170: layout.KEYCODE_BACKSLASH,
        173: layout.KEYCODE_EQUAL_SIGN,
        179: layout.KEYCODE_MEDIA_PLAY_PAUSE,
        168: layout.KEYCODE_REFRESH,
        186: layout.KEYCODE_SEMICOLON,
        187: layout.KEYCODE_EQUAL_SIGN,
        188: layout.KEYCODE_COMMA,
        189: layout.KEYCODE_MINUS,
        190: layout.KEYCODE_PERIOD,
        191: layout.KEYCODE_FORWARD_SLASH,
        192: layout.KEYCODE_ACCENT_GRAVE,
        219: layout.KEYCODE_LEFT_BRACKET,
        220: layout.KEYCODE_BACKSLASH,
        221: layout.KEYCODE_RIGHT_BRACKET,
        222: layout.KEYCODE_SINGLE_QUOTE,
        223: layout.KEYCODE_ACCENT_GRAVE,
        225: layout.KEYCODE_RIGHT_ALT,
    }


def _get_target_keyboard_layout(keyboard_layout_string):
    mappings = {
        'QWERTY': qwerty,
        'AZERTY': azerty,
    }
    try:
        return mappings[keyboard_layout_string.upper()]
    except KeyError:
        raise InvalidKeyboardLayout('Unrecognized keyboard layout: %s' %
                                    keyboard_layout_string)


def _map_modifier_keys(keystroke):
    modifier_bitmask = 0

    # HACK: Because JavaScript's keydown event doesn't indicate left or right
    # modifier unless it's the only key pressed, we special case it so that if
    # we see is_right_modifier set to true, we assume it's not a key
    # combination, but rather a modifier key in isolation, so we set only that
    # one modifier key.
    if keystroke.is_right_modifier:
        if keystroke.left_ctrl_modifier:
            return modifiers.RIGHT_CTRL
        elif keystroke.left_shift_modifier:
            return modifiers.RIGHT_SHIFT
        elif keystroke.left_alt_modifier:
            return modifiers.RIGHT_ALT
        elif keystroke.left_meta_modifier:
            return modifiers.RIGHT_META

    if keystroke.left_ctrl_modifier:
        modifier_bitmask |= modifiers.LEFT_CTRL
    if keystroke.left_shift_modifier:
        modifier_bitmask |= modifiers.LEFT_SHIFT
    if keystroke.left_alt_modifier:
        modifier_bitmask |= modifiers.LEFT_ALT
    if keystroke.left_meta_modifier:
        modifier_bitmask |= modifiers.LEFT_META
    if keystroke.right_alt_modifier:
        modifier_bitmask |= modifiers.RIGHT_ALT

    return modifier_bitmask
