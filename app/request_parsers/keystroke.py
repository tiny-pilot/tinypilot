import js_to_hid


class Error(Exception):
    pass


class MissingFieldErrorError(Error):
    pass


def parse_keystroke(message):
    if not isinstance(message, dict):
        raise MissingFieldErrorError(
            'Keystroke parameter is invalid, expecting a dictionary data type')
    if 'codes' not in message:
        raise MissingFieldErrorError(
            'Keystroke request is missing required field: codes')
    return js_to_hid.convert(message['codes'])
