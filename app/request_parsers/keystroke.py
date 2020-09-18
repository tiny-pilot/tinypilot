import dataclasses


class Error(Exception):
    pass


class InvalidModifierKey(Error):
    pass


class InvalidKeyCode(Error):
    pass


@dataclasses.dataclass
class Keystroke:
    id: int
    meta_modifier: bool
    alt_modifier: bool
    shift_modifier: bool
    ctrl_modifier: bool
    key: str
    key_code: int


def parse_keystroke(message):
    if not isinstance(message, dict):
        raise InvalidKeyCode(
            'Keystroke parameter is invalid, expecting a dictionary data type')
    missing_fields = [
        key for key in ('id', 'key', 'keyCode') if key not in message
    ]
    if len(missing_fields):
        raise InvalidKeyCode('Keystroke fields missing: %s' %
                             ', '.join(missing_fields))
    return Keystroke(
        id=message['id'],
        meta_modifier=_parse_modifier_key(message['metaKey'] if 'metaKey' in
                                          message else None),
        alt_modifier=_parse_modifier_key(message['altKey'] if 'altKey' in
                                         message else None),
        shift_modifier=_parse_modifier_key(message['shiftKey'] if 'shiftKey' in
                                           message else None),
        ctrl_modifier=_parse_modifier_key(message['ctrlKey'] if 'ctrlKey' in
                                          message else None),
        key=message['key'],
        key_code=_parse_key_code(message['keyCode']))


def _parse_modifier_key(modifier_key):
    if type(modifier_key) is not bool:
        raise InvalidModifierKey('Modifier keys must be boolean values: %s' %
                                 modifier_key)
    return modifier_key


def _parse_key_code(key_code):
    if type(key_code) is not int:
        raise InvalidKeyCode('Key code must be an integer value: %s' % key_code)
    if not (0 <= key_code <= 0xff):
        raise InvalidKeyCode('Key code must be between 0x00 and 0xff: %d',
                             key_code)
    return key_code
