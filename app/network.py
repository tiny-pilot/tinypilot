import dataclasses
import re
import subprocess

_CONFIG_FILE = '/etc/wpa_supplicant/wpa_supplicant.conf'
_WIFI_COUNTRY_PATTERN = re.compile(r'^\s*country=(.+)$')
_WIFI_SSID_PATTERN = re.compile(r'^\s*ssid="(.+)"$')


class Error(Exception):
    pass


class NetworkError(Error):
    pass


@dataclasses.dataclass
class NetworkStatus:
    ethernet: bool
    wifi: bool


@dataclasses.dataclass
class WiFiSettings:
    country_code: str
    ssid: str
    psk: str  # Optional.


def status():
    """Checks the connectivity of the network interfaces.

    Returns:
        NetworkStatus
    """
    network_status = NetworkStatus(False, False)
    try:
        with open('/sys/class/net/eth0/operstate', encoding='utf-8') as file:
            eth0 = file.read().strip()
            network_status.ethernet = eth0 == 'up'
        with open('/sys/class/net/wlan0/operstate', encoding='utf-8') as file:
            wlan0 = file.read().strip()
            network_status.wifi = wlan0 == 'up'
    except OSError:
        pass
    return network_status


def read_wifi_settings():
    """Determines the current WiFi settings (if present).

    Returns:
        WiFiSettings or None.
    """
    wifi = WiFiSettings(None, None, None)
    with open(_CONFIG_FILE, encoding='utf-8') as file:
        for line in file:
            match_country = _WIFI_COUNTRY_PATTERN.search(line.strip())
            if match_country:
                wifi.country_code = match_country.group(1)
                continue
            match_ssid = _WIFI_SSID_PATTERN.search(line.strip())
            if match_ssid:
                wifi.ssid = match_ssid.group(1)
                continue
    return wifi


def enable_wifi(wifi_settings):
    """Enables a wireless network connection.

    Args:
        wifi_settings: The desired settings.

    Raises:
        NetworkError
    """
    args = [
        'sudo', '/opt/tinypilot-privileged/scripts/enable-wifi', '--country',
        wifi_settings.country_code, '--ssid', wifi_settings.ssid
    ]
    if wifi_settings.psk:
        args.extend(['--psk', wifi_settings.psk])
    try:
        return subprocess.Popen(args)
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e


def disable_wifi():
    """Removes the WiFi settings and disables the wireless connection.

    Raises:
        NetworkError
    """
    try:
        return subprocess.Popen([
            'sudo',
            '/opt/tinypilot-privileged/scripts/disable-wifi',
        ])
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e
