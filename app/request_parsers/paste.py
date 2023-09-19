import text_to_hid
from request_parsers import errors
from request_parsers import json


def parse_keystrokes(request):
    """
    Parses HID keystrokes from the request.

    Args:
        request: Flask request with the following fields in the JSON body:
            (str) text
            (str) language

    Returns:
        A list of HID keystrokes.

    Raises:
        UnsupportedPastedCharacterError: If a pasted character cannot to be
            converted to a HID keystroke.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (text,
     language) = json.parse_json_body(request,
                                      required_fields=['text', 'language'])
    keystrokes = []
    # Preserve the ordering of any unsupported characters found.
    unsupported_chars_found = {}
    for char in text:
        try:
            keystroke = text_to_hid.convert(char, language)
        except text_to_hid.UnsupportedCharacterError:
            unsupported_chars_found[char] = True
            continue
        # Skip ignored characters.
        if keystroke is None:
            continue
        keystrokes.append(keystroke)
    if unsupported_chars_found:
        raise errors.UnsupportedPastedCharacterError(
            f'These characters are not supported: '
            f'{", ".join(map(repr, unsupported_chars_found.keys()))}')

    return keystrokes
