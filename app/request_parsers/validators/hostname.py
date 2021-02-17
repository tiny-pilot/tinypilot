import re

_HOSTNAME_PATTERN = re.compile(r'^[-0-9a-z]{1,63}$')


def validate(hostname):
    """
    Checks whether a hostname is valid according to the rules in
    https://man7.org/linux/man-pages/man7/hostname.7.html

    Args:
        hostname: A hostname as string.

    Returns:
        Whether or not the hostname is valid or not (bool).
    """
    if not isinstance(hostname, str):
        return False
    if hostname.startswith('-'):
        return False
    if _HOSTNAME_PATTERN.match(hostname) is None:
        return False
    return True
