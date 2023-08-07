import re

from hid import keycodes as hid


class Error(Exception):
    pass


class UnsupportedCharacterError(Error):
    pass


# Mappings of characters to codes that are shared among different keyboard
# layouts.
COMMON_CHAR_TO_HID_MAP = {
    "\t": hid.KEYCODE_TAB,
    "\n": hid.KEYCODE_ENTER,
    " ": hid.KEYCODE_SPACEBAR,
    "1": hid.KEYCODE_NUMBER_1,
    "2": hid.KEYCODE_NUMBER_2,
    "3": hid.KEYCODE_NUMBER_3,
    "4": hid.KEYCODE_NUMBER_4,
    "5": hid.KEYCODE_NUMBER_5,
    "6": hid.KEYCODE_NUMBER_6,
    "7": hid.KEYCODE_NUMBER_7,
    "8": hid.KEYCODE_NUMBER_8,
    "9": hid.KEYCODE_NUMBER_9,
    "0": hid.KEYCODE_NUMBER_0,
    "$": hid.KEYCODE_NUMBER_4,
    "!": hid.KEYCODE_NUMBER_1,
    "%": hid.KEYCODE_NUMBER_5,
    "^": hid.KEYCODE_NUMBER_6,
    "&": hid.KEYCODE_NUMBER_7,
    "*": hid.KEYCODE_NUMBER_8,
    "(": hid.KEYCODE_NUMBER_9,
    ")": hid.KEYCODE_NUMBER_0,
    "_": hid.KEYCODE_MINUS,
    "-": hid.KEYCODE_MINUS,
    "+": hid.KEYCODE_EQUAL_SIGN,
    "=": hid.KEYCODE_EQUAL_SIGN,
    ":": hid.KEYCODE_SEMICOLON,
    ";": hid.KEYCODE_SEMICOLON,
    "a": hid.KEYCODE_A,
    "b": hid.KEYCODE_B,
    "c": hid.KEYCODE_C,
    "d": hid.KEYCODE_D,
    "e": hid.KEYCODE_E,
    "f": hid.KEYCODE_F,
    "g": hid.KEYCODE_G,
    "h": hid.KEYCODE_H,
    "i": hid.KEYCODE_I,
    "j": hid.KEYCODE_J,
    "k": hid.KEYCODE_K,
    "l": hid.KEYCODE_L,
    "m": hid.KEYCODE_M,
    "n": hid.KEYCODE_N,
    "o": hid.KEYCODE_O,
    "p": hid.KEYCODE_P,
    "q": hid.KEYCODE_Q,
    "r": hid.KEYCODE_R,
    "s": hid.KEYCODE_S,
    "t": hid.KEYCODE_T,
    "u": hid.KEYCODE_U,
    "v": hid.KEYCODE_V,
    "w": hid.KEYCODE_W,
    "x": hid.KEYCODE_X,
    "y": hid.KEYCODE_Y,
    "z": hid.KEYCODE_Z,
    ",": hid.KEYCODE_COMMA,
    "<": hid.KEYCODE_COMMA,
    ".": hid.KEYCODE_PERIOD,
    ">": hid.KEYCODE_PERIOD,
    "/": hid.KEYCODE_FORWARD_SLASH,
    "?": hid.KEYCODE_FORWARD_SLASH,
    "[": hid.KEYCODE_LEFT_BRACKET,
    "{": hid.KEYCODE_LEFT_BRACKET,
    "]": hid.KEYCODE_RIGHT_BRACKET,
    "}": hid.KEYCODE_RIGHT_BRACKET,
    "'": hid.KEYCODE_SINGLE_QUOTE,
}

US_CHAR_TO_HID_MAP = COMMON_CHAR_TO_HID_MAP | {
    "@": hid.KEYCODE_NUMBER_2,
    "#": hid.KEYCODE_NUMBER_3,
    "~": hid.KEYCODE_ACCENT_GRAVE,
    "`": hid.KEYCODE_ACCENT_GRAVE,
    "\\": hid.KEYCODE_BACKSLASH,
    "|": hid.KEYCODE_BACKSLASH,
    "\"": hid.KEYCODE_SINGLE_QUOTE,
}

GB_CHAR_TO_HID_MAP = COMMON_CHAR_TO_HID_MAP | {
    "\"": hid.KEYCODE_NUMBER_2,
    "£": hid.KEYCODE_NUMBER_3,
    "\\": hid.KEYCODE_102ND,
    "|": hid.KEYCODE_102ND,
    "~": hid.KEYCODE_BACKSLASH,
    "#": hid.KEYCODE_BACKSLASH,
    "`": hid.KEYCODE_ACCENT_GRAVE,
    "¬": hid.KEYCODE_ACCENT_GRAVE,
    "@": hid.KEYCODE_SINGLE_QUOTE,
}

# TODO(jason): Make more robust.
# I think this might be wrong and depends on the chosen language. It's just a
# matter of time before shifted and non-shifted characters start conflicting.
NEEDS_SHIFT_REGEX = re.compile(r'[A-Z¬!"£$%^&*()_+{}|<>?:@~#]')


def convert(char, language):
    """Converts a language character into a HID modifier and keycode."""
    try:
        language_map = {
            "en-GB": GB_CHAR_TO_HID_MAP,
            "en-US": US_CHAR_TO_HID_MAP
        }[language]
    except KeyError:
        # Default to en-US if no other language matches.
        language_map = US_CHAR_TO_HID_MAP

    try:
        hid_keycode = language_map[char.lower()]
    except KeyError as e:
        raise UnsupportedCharacterError(
            f"Unsupported character {char.lower()}") from e

    if NEEDS_SHIFT_REGEX.match(char):
        hid_modifier = hid.MODIFIER_LEFT_SHIFT
    else:
        hid_modifier = hid.KEYCODE_NONE

    return hid_modifier, hid_keycode
