class Error(Exception):
    pass


class MalformedRequestError(Error):
    pass


class MissingFieldError(Error):
    pass


class InvalidUsernameError(Error):
    pass


class InvalidPasswordError(Error):
    pass


class InvalidHostnameError(Error):
    code = 'INVALID_HOSTNAME'


class InvalidWifiSettings(Error):
    code = 'INVALID_WIFI_SETTINGS'


class InvalidRequiresHttpsPropError(Error):
    pass


class InvalidVideoSettingError(Error):
    pass


class InvalidVideoSettingStunAddressError(Error):
    code = 'INVALID_STUN_ADDRESS'


class UnsupportedPastedCharacterError(Error):
    pass


class InvalidUserRoleError(Error):
    pass
