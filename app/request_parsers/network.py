import network
from request_parsers import errors
from request_parsers import json


def parse_wifi_settings(request):
    """Parses WiFi settings from the request.

    Returns:
        WiFiSettings

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
        raise errors.InvalidWifiSettings('The country code is not a string.')
    if len(country_code) != 2:
        raise errors.InvalidWifiSettings(
            'The country code must consist of 2 characters.')
    if not country_code.isalpha():
        raise errors.InvalidWifiSettings(
            'The country code must only contain letters.')

    if not isinstance(ssid, str):
        raise errors.InvalidWifiSettings('The SSID is not a string.')
    if len(ssid) == 0:
        raise errors.InvalidWifiSettings('The SSID cannot be empty.')

    if psk is not None:
        if not isinstance(psk, str):
            raise errors.InvalidWifiSettings('The password is not a string.')
        if len(psk) < 8 or len(psk) > 63:
            raise errors.InvalidWifiSettings(
                'The password must consist of 8-63 characters.')

    return network.WiFiSettings(country_code.upper(), ssid, psk)
