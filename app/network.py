import dataclasses
import subprocess


class Error(Exception):
    pass


class WifiApplyError(Error):
    pass


@dataclasses.dataclass
class NetworkStatus:
    ethernet: bool
    wifi: bool


@dataclasses.dataclass
class WiFiSettings:
    country_code: str
    ssid: str
    psk: str


def status():
    """...
    """
    network_status = NetworkStatus(False, False)

    try:
        with open('/sys/class/net/eth0/operstate') as f:
            eth0 = f.read().strip()
            network_status.ethernet = eth0 == 'up'
    except OSError:
        pass
    try:
        with open('/sys/class/net/wlan0/operstate') as f:
            wlan0 = f.read().strip()
            network_status.wifi = wlan0 == 'up'
    except OSError:
        pass

    return network_status


def read_wifi_settings():
    """...
    """
    # TODO parse from wpa_supplicant.conf file
    return WiFiSettings('US', 'wlan-184722', None)


def enable_wifi(wifi_settings):
    """...
    """
    try:
        return subprocess.Popen([
            'sudo', '/opt/tinypilot-privileged/scripts/enable-wifi',
            '--country', wifi_settings.country_code,
            '--ssid', wifi_settings.ssid,
            '--psk', wifi_settings.psk
        ])
    except subprocess.CalledProcessError as e:
        raise WifiApplyError(str(e.output).strip()) from e


def disable_wifi():
    """...
    """
    try:
        return subprocess.Popen([
            'sudo', '/opt/tinypilot-privileged/scripts/disable-wifi',
        ])
    except subprocess.CalledProcessError as e:
        raise WifiApplyError(str(e.output).strip()) from e
