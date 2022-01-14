import re

from request_parsers import errors
from request_parsers import message as message_parser

_HOSTNAME_PATTERN = re.compile(r'^[-0-9a-z]{1,63}$')


def parse_hostname(request):
    """
    Parses the hostname property from the request.
    Checks whether the hostname is valid according to the rules in
    https://man7.org/linux/man-pages/man7/hostname.7.html

    Args:
        request: Flask request with the hostname field as string.

    Returns:
        The parsed and validated hostname (as string).

    Raises:
        InvalidHostnameError: If the hostname is invalid.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (hostname,) = message_parser.parse_json_body(request,
                                                 required_fields=['hostname'])

    if not isinstance(hostname, str):
        raise errors.InvalidHostnameError('The hostname is not a string.')
    if hostname == 'localhost':
        raise errors.InvalidHostnameError('The hostname cannot be localhost.')
    if hostname.startswith('-'):
        raise errors.InvalidHostnameError('The hostname cannot start with "-".')
    if _HOSTNAME_PATTERN.match(hostname) is None:
        raise errors.InvalidHostnameError(
            'The hostname contains invalid characters.')

    return hostname
