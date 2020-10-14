import dataclasses


class Error(Exception):
    pass


class MissingField(Error):
    pass


class InvalidModifierKey(Error):
    pass


class InvalidKeyCode(Error):
    pass


class InvalidLocation(Error):
    pass


@dataclasses.dataclass
class Keystroke:
    left_ctrl_modifier: bool
    left_shift_modifier: bool
    left_alt_modifier: bool
    left_meta_modifier: bool
    right_alt_modifier: bool
    key: str
    key_code: int
    is_right_modifier: bool


def parse_keystroke(message):
    if not isinstance(message, dict):
        raise MissingField(
            'Keystroke parameter is invalid, expecting a dictionary data type')
    required_fields = (
        'key',
        'keyCode',
        'location',
        'ctrlKey',
        'shiftKey',
        'altKey',
        'metaKey',
        'altGraphKey',
    )
    for field in required_fields:
        if field not in message:
            raise MissingField(
                'Keystroke request is missing required field: %s' % field)
    return Keystroke(
        left_ctrl_modifier=_parse_modifier_key(message['ctrlKey']),
        left_shift_modifier=_parse_modifier_key(message['shiftKey']),
        left_alt_modifier=_parse_modifier_key(message['altKey']),
        left_meta_modifier=_parse_modifier_key(message['metaKey']),
        right_alt_modifier=_parse_modifier_key(message['altGraphKey']),
        key=message['key'],
        key_code=_parse_key_code(message['keyCode']),
        is_right_modifier=_parse_is_right_key_location(message['location']))


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


def _parse_is_right_key_location(location):
    if location is None:
        return False
    if type(location) is not str:
        raise InvalidLocation('Location must be "left", "right", or null.')
    elif location.lower() == 'left':
        return False
    elif location.lower() == 'right':
        return True
    raise InvalidLocation('Location must be "left", "right", or null.')
