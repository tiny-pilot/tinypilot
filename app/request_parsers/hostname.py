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
        The parsed hostname.

    Raises:
        InvalidHostnameError: If the hostname is invalid.
    """
    message = message_parser.parse_message(request,
                                           required_fields=['hostname'])
    hostname = message['hostname']

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
