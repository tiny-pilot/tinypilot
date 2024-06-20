import network
from request_parsers import json


def parse_wifi_settings(request):
    """...
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (country_code, ssid, psk,) = json.parse_json_body(request, required_fields=['countryCode', 'ssid', 'psk'])
    return network.WiFiSettings(country_code, ssid, psk)
