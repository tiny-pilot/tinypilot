import dataclasses
import re
import subprocess

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
class WifiSettings:
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
    except OSError:
        pass  # We treat this as if the interface was down altogether.
    try:
        with open('/sys/class/net/wlan0/operstate', encoding='utf-8') as file:
            wlan0 = file.read().strip()
            network_status.wifi = wlan0 == 'up'
    except OSError:
        pass  # We treat this as if the interface was down altogether.
    return network_status


def determine_wifi_settings():
    """Determines the current WiFi settings (if set).

    Returns:
        WifiSettings: if the `ssid` and `country_code` attributes are `None`,
            there is no WiFi configuration present. The `psk` property is
            always `None` for security reasons.
    """
    try:
        # We cannot read the wpa_supplicant.conf file directly, because it is
        # owned by the root user.
        config_lines = subprocess.check_output([
            'sudo', '/opt/tinypilot-privileged/scripts/print-marker-sections',
            '/etc/wpa_supplicant/wpa_supplicant.conf'
        ],
                                               stderr=subprocess.STDOUT,
                                               universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e

    wifi = WifiSettings(None, None, None)
    for line in config_lines.splitlines():
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

    Note: The function is executed in a "fire and forget" manner, to prevent
    the HTTP request from failing erratically due to a network interruption.

    Args:
        wifi_settings: The new, desired settings (of type WifiSettings)

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
        # Ignore pylint since we're not managing the child process.
        # pylint: disable=consider-using-with
        subprocess.Popen(args)
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e


def disable_wifi():
    """Removes the WiFi settings and disables the wireless connection.

    Note: The function is executed in a "fire and forget" manner, to prevent
    the HTTP request from failing erratically due to a network interruption.

    Raises:
        NetworkError
    """
    try:
        # Ignore pylint since we're not managing the child process.
        # pylint: disable=consider-using-with
        subprocess.Popen([
            'sudo',
            '/opt/tinypilot-privileged/scripts/disable-wifi',
        ])
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e
