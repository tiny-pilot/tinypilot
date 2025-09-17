import re

from request_parsers import errors

_USERNAME_PATTERN = re.compile(r'^[a-z0-9.\-_]*$', re.IGNORECASE)


def parse_username(username):
    if not isinstance(username, str):
        raise errors.InvalidUsernameError('Username must be a string')
    if not (1 <= len(username) <= 20):
        raise errors.InvalidUsernameError('Username must be 1-20 characters in'
                                          ' length')
    if not _USERNAME_PATTERN.match(username):
        raise errors.InvalidUsernameError(
            'Username can only contain characters a-z, A-Z, 0-9, or .-_')

    return username
