from hid import keycodes as hid


class Error(Exception):
    pass


class UnsupportedCharacterError(Error):
    pass


# Mappings of characters to codes that are shared among different keyboard
# layouts.
_COMMON_CHAR_TO_HID_MAP = {
    '\r':
        None,
    '\t':
        hid.Keystroke(keycodes=[hid.KEYCODE_TAB]),
    '\n':
        hid.Keystroke(keycodes=[hid.KEYCODE_ENTER]),
    ' ':
        hid.Keystroke(keycodes=[hid.KEYCODE_SPACEBAR]),
    '1':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_1]),
    '2':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_2]),
    '3':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_3]),
    '4':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_4]),
    '5':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_5]),
    '6':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_6]),
    '7':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_7]),
    '8':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_8]),
    '9':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_9]),
    '0':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_0]),
    '$':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_4],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '!':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_1],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '%':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_5],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '^':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_6],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '&':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_7],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '*':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_8],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '(':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_9],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    ')':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_0],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '_':
        hid.Keystroke(keycodes=[hid.KEYCODE_MINUS],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '-':
        hid.Keystroke(keycodes=[hid.KEYCODE_MINUS]),
    '+':
        hid.Keystroke(keycodes=[hid.KEYCODE_EQUAL_SIGN],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '=':
        hid.Keystroke(keycodes=[hid.KEYCODE_EQUAL_SIGN]),
    ':':
        hid.Keystroke(keycodes=[hid.KEYCODE_SEMICOLON],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    ';':
        hid.Keystroke(keycodes=[hid.KEYCODE_SEMICOLON]),
    'a':
        hid.Keystroke(keycodes=[hid.KEYCODE_A]),
    'b':
        hid.Keystroke(keycodes=[hid.KEYCODE_B]),
    'c':
        hid.Keystroke(keycodes=[hid.KEYCODE_C]),
    'd':
        hid.Keystroke(keycodes=[hid.KEYCODE_D]),
    'e':
        hid.Keystroke(keycodes=[hid.KEYCODE_E]),
    'f':
        hid.Keystroke(keycodes=[hid.KEYCODE_F]),
    'g':
        hid.Keystroke(keycodes=[hid.KEYCODE_G]),
    'h':
        hid.Keystroke(keycodes=[hid.KEYCODE_H]),
    'i':
        hid.Keystroke(keycodes=[hid.KEYCODE_I]),
    'j':
        hid.Keystroke(keycodes=[hid.KEYCODE_J]),
    'k':
        hid.Keystroke(keycodes=[hid.KEYCODE_K]),
    'l':
        hid.Keystroke(keycodes=[hid.KEYCODE_L]),
    'm':
        hid.Keystroke(keycodes=[hid.KEYCODE_M]),
    'n':
        hid.Keystroke(keycodes=[hid.KEYCODE_N]),
    'o':
        hid.Keystroke(keycodes=[hid.KEYCODE_O]),
    'p':
        hid.Keystroke(keycodes=[hid.KEYCODE_P]),
    'q':
        hid.Keystroke(keycodes=[hid.KEYCODE_Q]),
    'r':
        hid.Keystroke(keycodes=[hid.KEYCODE_R]),
    's':
        hid.Keystroke(keycodes=[hid.KEYCODE_S]),
    't':
        hid.Keystroke(keycodes=[hid.KEYCODE_T]),
    'u':
        hid.Keystroke(keycodes=[hid.KEYCODE_U]),
    'v':
        hid.Keystroke(keycodes=[hid.KEYCODE_V]),
    'w':
        hid.Keystroke(keycodes=[hid.KEYCODE_W]),
    'x':
        hid.Keystroke(keycodes=[hid.KEYCODE_X]),
    'y':
        hid.Keystroke(keycodes=[hid.KEYCODE_Y]),
    'z':
        hid.Keystroke(keycodes=[hid.KEYCODE_Z]),
    'A':
        hid.Keystroke(keycodes=[hid.KEYCODE_A],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'B':
        hid.Keystroke(keycodes=[hid.KEYCODE_B],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'C':
        hid.Keystroke(keycodes=[hid.KEYCODE_C],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'D':
        hid.Keystroke(keycodes=[hid.KEYCODE_D],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'E':
        hid.Keystroke(keycodes=[hid.KEYCODE_E],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'F':
        hid.Keystroke(keycodes=[hid.KEYCODE_F],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'G':
        hid.Keystroke(keycodes=[hid.KEYCODE_G],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'H':
        hid.Keystroke(keycodes=[hid.KEYCODE_H],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'I':
        hid.Keystroke(keycodes=[hid.KEYCODE_I],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'J':
        hid.Keystroke(keycodes=[hid.KEYCODE_J],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'K':
        hid.Keystroke(keycodes=[hid.KEYCODE_K],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'L':
        hid.Keystroke(keycodes=[hid.KEYCODE_L],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'M':
        hid.Keystroke(keycodes=[hid.KEYCODE_M],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'N':
        hid.Keystroke(keycodes=[hid.KEYCODE_N],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'O':
        hid.Keystroke(keycodes=[hid.KEYCODE_O],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'P':
        hid.Keystroke(keycodes=[hid.KEYCODE_P],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'Q':
        hid.Keystroke(keycodes=[hid.KEYCODE_Q],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'R':
        hid.Keystroke(keycodes=[hid.KEYCODE_R],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'S':
        hid.Keystroke(keycodes=[hid.KEYCODE_S],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'T':
        hid.Keystroke(keycodes=[hid.KEYCODE_T],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'U':
        hid.Keystroke(keycodes=[hid.KEYCODE_U],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'V':
        hid.Keystroke(keycodes=[hid.KEYCODE_V],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'W':
        hid.Keystroke(keycodes=[hid.KEYCODE_W],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'X':
        hid.Keystroke(keycodes=[hid.KEYCODE_X],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'Y':
        hid.Keystroke(keycodes=[hid.KEYCODE_Y],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    'Z':
        hid.Keystroke(keycodes=[hid.KEYCODE_Z],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    ',':
        hid.Keystroke(keycodes=[hid.KEYCODE_COMMA]),
    '<':
        hid.Keystroke(keycodes=[hid.KEYCODE_COMMA],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '.':
        hid.Keystroke(keycodes=[hid.KEYCODE_PERIOD]),
    '>':
        hid.Keystroke(keycodes=[hid.KEYCODE_PERIOD],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '/':
        hid.Keystroke(keycodes=[hid.KEYCODE_FORWARD_SLASH]),
    '?':
        hid.Keystroke(keycodes=[hid.KEYCODE_FORWARD_SLASH],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '[':
        hid.Keystroke(keycodes=[hid.KEYCODE_LEFT_BRACKET]),
    '{':
        hid.Keystroke(keycodes=[hid.KEYCODE_LEFT_BRACKET],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    ']':
        hid.Keystroke(keycodes=[hid.KEYCODE_RIGHT_BRACKET]),
    '}':
        hid.Keystroke(keycodes=[hid.KEYCODE_RIGHT_BRACKET],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '\'':
        hid.Keystroke(keycodes=[hid.KEYCODE_SINGLE_QUOTE]),
}

_US_CHAR_TO_HID_MAP = _COMMON_CHAR_TO_HID_MAP | {
    '@':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_2],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '#':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_3],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '~':
        hid.Keystroke(keycodes=[hid.KEYCODE_ACCENT_GRAVE],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '`':
        hid.Keystroke(keycodes=[hid.KEYCODE_ACCENT_GRAVE]),
    '\\':
        hid.Keystroke(keycodes=[hid.KEYCODE_BACKSLASH]),
    '|':
        hid.Keystroke(keycodes=[hid.KEYCODE_BACKSLASH],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '"':
        hid.Keystroke(keycodes=[hid.KEYCODE_SINGLE_QUOTE],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
}

_GB_CHAR_TO_HID_MAP = _COMMON_CHAR_TO_HID_MAP | {
    '"':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_2],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '£':
        hid.Keystroke(keycodes=[hid.KEYCODE_NUMBER_3],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '\\':
        hid.Keystroke(keycodes=[hid.KEYCODE_102ND]),
    '|':
        hid.Keystroke(keycodes=[hid.KEYCODE_102ND],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '~':
        hid.Keystroke(keycodes=[hid.KEYCODE_BACKSLASH],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '#':
        hid.Keystroke(keycodes=[hid.KEYCODE_BACKSLASH],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '`':
        hid.Keystroke(keycodes=[hid.KEYCODE_ACCENT_GRAVE]),
    '¬':
        hid.Keystroke(keycodes=[hid.KEYCODE_ACCENT_GRAVE],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
    '@':
        hid.Keystroke(keycodes=[hid.KEYCODE_SINGLE_QUOTE],
                      modifier=hid.MODIFIER_LEFT_SHIFT),
}


def convert(char, language):
    """Converts a language character into a HID Keystroke object.

    Args:
        char: A single character as a string.
        language: An IETF language tag as a string.

    Returns:
        A HID Keystroke object.

    Raises:
        UnsupportedCharacterError: If the character is not supported.
    """
    try:
        language_map = {
            'en-GB': _GB_CHAR_TO_HID_MAP,
            'en-US': _US_CHAR_TO_HID_MAP
        }[language]
    except KeyError:
        # Default to en-US if no other language matches.
        language_map = _US_CHAR_TO_HID_MAP

    try:
        hid_keystroke = language_map[char]
    except KeyError as e:
        raise UnsupportedCharacterError(f'Unsupported character {char}') from e

    return hid_keystroke
