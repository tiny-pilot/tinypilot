import re

from hid import keycodes as hid


class Error(Exception):
    pass


class UnsupportedCharacterError(Error):
    pass


# Mappings of characters to codes that are shared among different keyboard
# layouts.
COMMON_CHAR_TO_HID_MAP = {
    "\t": hid.Keystroke(keycode=hid.KEYCODE_TAB),
    "\n": hid.Keystroke(keycode=hid.KEYCODE_ENTER),
    " ": hid.Keystroke(keycode=hid.KEYCODE_SPACEBAR),
    "1": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_1),
    "2": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_2),
    "3": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_3),
    "4": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_4),
    "5": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_5),
    "6": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_6),
    "7": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_7),
    "8": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_8),
    "9": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_9),
    "0": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_0),
    "$": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_4),
    "!": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_1),
    "%": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_5),
    "^": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_6),
    "&": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_7),
    "*": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_8),
    "(": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_9),
    ")": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_0),
    "_": hid.Keystroke(keycode=hid.KEYCODE_MINUS),
    "-": hid.Keystroke(keycode=hid.KEYCODE_MINUS),
    "+": hid.Keystroke(keycode=hid.KEYCODE_EQUAL_SIGN),
    "=": hid.Keystroke(keycode=hid.KEYCODE_EQUAL_SIGN),
    ":": hid.Keystroke(keycode=hid.KEYCODE_SEMICOLON),
    ";": hid.Keystroke(keycode=hid.KEYCODE_SEMICOLON),
    "a": hid.Keystroke(keycode=hid.KEYCODE_A),
    "b": hid.Keystroke(keycode=hid.KEYCODE_B),
    "c": hid.Keystroke(keycode=hid.KEYCODE_C),
    "d": hid.Keystroke(keycode=hid.KEYCODE_D),
    "e": hid.Keystroke(keycode=hid.KEYCODE_E),
    "f": hid.Keystroke(keycode=hid.KEYCODE_F),
    "g": hid.Keystroke(keycode=hid.KEYCODE_G),
    "h": hid.Keystroke(keycode=hid.KEYCODE_H),
    "i": hid.Keystroke(keycode=hid.KEYCODE_I),
    "j": hid.Keystroke(keycode=hid.KEYCODE_J),
    "k": hid.Keystroke(keycode=hid.KEYCODE_K),
    "l": hid.Keystroke(keycode=hid.KEYCODE_L),
    "m": hid.Keystroke(keycode=hid.KEYCODE_M),
    "n": hid.Keystroke(keycode=hid.KEYCODE_N),
    "o": hid.Keystroke(keycode=hid.KEYCODE_O),
    "p": hid.Keystroke(keycode=hid.KEYCODE_P),
    "q": hid.Keystroke(keycode=hid.KEYCODE_Q),
    "r": hid.Keystroke(keycode=hid.KEYCODE_R),
    "s": hid.Keystroke(keycode=hid.KEYCODE_S),
    "t": hid.Keystroke(keycode=hid.KEYCODE_T),
    "u": hid.Keystroke(keycode=hid.KEYCODE_U),
    "v": hid.Keystroke(keycode=hid.KEYCODE_V),
    "w": hid.Keystroke(keycode=hid.KEYCODE_W),
    "x": hid.Keystroke(keycode=hid.KEYCODE_X),
    "y": hid.Keystroke(keycode=hid.KEYCODE_Y),
    "z": hid.Keystroke(keycode=hid.KEYCODE_Z),
    ",": hid.Keystroke(keycode=hid.KEYCODE_COMMA),
    "<": hid.Keystroke(keycode=hid.KEYCODE_COMMA),
    ".": hid.Keystroke(keycode=hid.KEYCODE_PERIOD),
    ">": hid.Keystroke(keycode=hid.KEYCODE_PERIOD),
    "/": hid.Keystroke(keycode=hid.KEYCODE_FORWARD_SLASH),
    "?": hid.Keystroke(keycode=hid.KEYCODE_FORWARD_SLASH),
    "[": hid.Keystroke(keycode=hid.KEYCODE_LEFT_BRACKET),
    "{": hid.Keystroke(keycode=hid.KEYCODE_LEFT_BRACKET),
    "]": hid.Keystroke(keycode=hid.KEYCODE_RIGHT_BRACKET),
    "}": hid.Keystroke(keycode=hid.KEYCODE_RIGHT_BRACKET),
    "'": hid.Keystroke(keycode=hid.KEYCODE_SINGLE_QUOTE),
}

US_CHAR_TO_HID_MAP = COMMON_CHAR_TO_HID_MAP | {
    "@": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_2),
    "#": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_3),
    "~": hid.Keystroke(keycode=hid.KEYCODE_ACCENT_GRAVE),
    "`": hid.Keystroke(keycode=hid.KEYCODE_ACCENT_GRAVE),
    "\\": hid.Keystroke(keycode=hid.KEYCODE_BACKSLASH),
    "|": hid.Keystroke(keycode=hid.KEYCODE_BACKSLASH),
    "\"": hid.Keystroke(keycode=hid.KEYCODE_SINGLE_QUOTE),
}

GB_CHAR_TO_HID_MAP = COMMON_CHAR_TO_HID_MAP | {
    "\"": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_2),
    "£": hid.Keystroke(keycode=hid.KEYCODE_NUMBER_3),
    "\\": hid.Keystroke(keycode=hid.KEYCODE_102ND),
    "|": hid.Keystroke(keycode=hid.KEYCODE_102ND),
    "~": hid.Keystroke(keycode=hid.KEYCODE_BACKSLASH),
    "#": hid.Keystroke(keycode=hid.KEYCODE_BACKSLASH),
    "`": hid.Keystroke(keycode=hid.KEYCODE_ACCENT_GRAVE),
    "¬": hid.Keystroke(keycode=hid.KEYCODE_ACCENT_GRAVE),
    "@": hid.Keystroke(keycode=hid.KEYCODE_SINGLE_QUOTE),
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
        hid_keystroke = language_map[char.lower()]
    except KeyError as e:
        raise UnsupportedCharacterError(
            f"Unsupported character {char.lower()}") from e

    if NEEDS_SHIFT_REGEX.match(char):
        hid_modifier = hid.MODIFIER_LEFT_SHIFT
    else:
        hid_modifier = hid.KEYCODE_NONE

    return hid_modifier, hid_keystroke.keycode
