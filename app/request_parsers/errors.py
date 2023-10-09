class Error(Exception):
    pass


class MalformedRequestError(Error):
    pass


class MissingFieldError(Error):
    pass


class InvalidHostnameError(Error):
    code = 'INVALID_HOSTNAME'


class InvalidVideoSettingError(Error):
    pass


class InvalidVideoSettingStunAddressError(Error):
    code = 'INVALID_STUN_ADDRESS'


class UnsupportedPastedCharacterError(Error):
    pass
