import network
from request_parsers import errors
from request_parsers import json


def parse_wifi_settings(request):
    """Parses WiFi settings from the request.

    Returns:
        WifiSettings

    Raises:
        InvalidWifiSettings
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (
        country_code,
        ssid,
        psk,
    ) = json.parse_json_body(request,
                             required_fields=['countryCode', 'ssid', 'psk'])

    if not isinstance(country_code, str):
        raise errors.InvalidWifiSettings('The country code must be a string.')
    if len(country_code) != 2:
        # The ISO 3166-1 alpha-2 standard theoretically allows any 2-digit
        # combination, so we don’t have to eagerly restrict this.
        raise errors.InvalidWifiSettings(
            'The country code must consist of 2 characters.')
    if not country_code.isalpha():
        raise errors.InvalidWifiSettings(
            'The country code must only contain letters.')

    if not isinstance(ssid, str):
        raise errors.InvalidWifiSettings('The SSID must be a string.')
    if len(ssid) == 0:
        raise errors.InvalidWifiSettings('The SSID cannot be empty.')

    if psk is not None:
        if not isinstance(psk, str):
            raise errors.InvalidWifiSettings('The password must be a string.')
        if len(psk) < 8 or len(psk) > 63:
            # Note: this constraint is imposed by the WPA2 standard. We need
            # to enforce this to prevent underlying commands from failing.
            raise errors.InvalidWifiSettings(
                'The password must consist of 8-63 characters.')

    return network.WifiSettings(country_code.upper(), ssid, psk)
