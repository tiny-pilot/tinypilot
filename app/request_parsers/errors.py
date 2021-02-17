class Error(Exception):
    pass


class MalformedRequest(Error):
    pass


class MissingField(Error):
    pass


class InvalidHostname(Error):
    pass
