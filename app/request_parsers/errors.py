class Error(Exception):
    pass


class MalformedRequestError(Error):
    pass


class MissingFieldError(Error):
    pass


class InvalidHostnameError(Error):
    code = "INVALID_HOSTNAME"


class InvalidVideoFpsError(Error):
    pass


class InvalidVideoJpegQualityError(Error):
    pass


class InvalidVideoStreamingModeError(Error):
    pass
