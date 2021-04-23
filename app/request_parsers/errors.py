class Error(Exception):
    pass


class MalformedRequestError(Error):
    pass


class MissingFieldError(Error):
    pass


class InvalidHostnameError(Error):
    pass


class InvalidVideoFpsError(Error):
    pass


class InvalidVideoJpegQualityError(Error):
    pass
