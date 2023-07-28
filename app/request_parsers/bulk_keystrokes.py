from request_parsers.keystroke import parse_keystroke
from request_parsers import json

import dataclasses

import js_to_hid


@dataclasses.dataclass
class HidKeystroke:
    modifier: int
    keycode: int


def parse_keystrokes(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (keystroke_messages,) = json.parse_json_body(request,
                                                 required_fields=['keystrokes'])
    keystrokes = []
    for keystroke_message in keystroke_messages:
        js_keystroke = parse_keystroke(keystroke_message)
        modifier, keycode = js_to_hid.convert(js_keystroke)
        hid_keystroke = HidKeystroke(modifier, keycode)
        keystrokes.append(hid_keystroke)
    return keystrokes
