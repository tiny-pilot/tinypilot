import datetime

_ISO_8601_FORMAT = '%Y-%m-%dT%H%M%SZ'


def to_string(dt):
    """Formats a datetime to ISO-8601 format.

    Args:
        dt: A datetime object (assumed to be in UTC time).

    Returns:
        An ISO-8601 formatted string (e.g., '2021-02-10T085735Z').
    """
    return dt.strftime(_ISO_8601_FORMAT)


def parse(iso_8601_string):
    """Parses an ISO-8601-formatted string into a datetime object.

    Args:
        iso_8601_string: The ISO-8601-formatted string to parse (e.g.,
            '2021-02-10T085735Z').

    Returns:
        A datetime object corresponding to the input string in UTC timezone.
    """
    return datetime.datetime.strptime(
        iso_8601_string, _ISO_8601_FORMAT).replace(tzinfo=datetime.timezone.utc)
