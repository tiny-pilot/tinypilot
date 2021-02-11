import datetime


def now():
    """Returns a timezone-aware datetime for the current time in UTC."""
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
