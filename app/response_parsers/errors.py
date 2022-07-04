class Error(Exception):
    pass


class MalformedResponseError(Error):
    pass


class MissingFieldError(Error):
    pass
