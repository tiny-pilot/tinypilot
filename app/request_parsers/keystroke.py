import dataclasses


class Error(Exception):
    pass


class MissingFieldErrorError(Error):
    pass


class InvalidModifierKeyError(Error):
    pass


class InvalidKeyCodeError(Error):
    pass


class InvalidLocationError(Error):
    pass


@dataclasses.dataclass
class Keystroke:
    # TODO(jotaen) Rename all modifiers to `ctrl_left_...` etc. instead of
    #              `left_ctrl_...` to make the naming consistent.
    left_ctrl_modifier: bool
    right_ctrl_modifier: bool
    left_shift_modifier: bool
    right_shift_modifier: bool
    left_alt_modifier: bool
    right_alt_modifier: bool
    left_meta_modifier: bool
    right_meta_modifier: bool
    key: str
    code: str


def parse_keystroke(message):
    if not isinstance(message, dict):
        raise MissingFieldErrorError(
            'Keystroke parameter is invalid, expecting a dictionary data type')
    required_fields = (
        'key',
        'code',
        'ctrlLeft',
        'ctrlRight',
        'shiftLeft',
        'shiftRight',
        'altLeft',
        'altRight',
        'metaLeft',
        'metaRight',
    )
    for field in required_fields:
        if field not in message:
            raise MissingFieldErrorError(
                'Keystroke request is missing required field: %s' % field)
    return Keystroke(
        left_ctrl_modifier=_parse_modifier_key(message['ctrlLeft']),
        right_ctrl_modifier=_parse_modifier_key(message['ctrlRight']),
        left_shift_modifier=_parse_modifier_key(message['shiftLeft']),
        right_shift_modifier=_parse_modifier_key(message['shiftRight']),
        left_alt_modifier=_parse_modifier_key(message['altLeft']),
        right_alt_modifier=_parse_modifier_key(message['altRight']),
        left_meta_modifier=_parse_modifier_key(message['metaLeft']),
        right_meta_modifier=_parse_modifier_key(message['metaRight']),
        key=message['key'],
        code=_parse_code(message['code']))


def _parse_modifier_key(modifier_key):
    if not isinstance(modifier_key, bool):
        raise InvalidModifierKeyError(
            'Modifier keys must be boolean values: %s' % modifier_key)
    return modifier_key


def _parse_code(code):
    if not isinstance(code, str):
        raise InvalidKeyCodeError('Key code must be a string: %s' % code)

    # Arbitrary limit, but just to prevent anything crazy.
    if len(code) > 30:
        raise InvalidKeyCodeError('Key code is too long: %s' % code)
    return code
