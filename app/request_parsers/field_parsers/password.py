from request_parsers import errors

_MIN_PASSWORD_LENGTH = 6
_MAX_PASSWORD_LENGTH = 60


def parse_password(password):
    if not isinstance(password, str):
        raise errors.InvalidPasswordError('Password must be a string')

    if not _MIN_PASSWORD_LENGTH <= len(password) <= _MAX_PASSWORD_LENGTH:
        raise errors.InvalidPasswordError(
            'Password must be 6-60 characters in length')

    return password
