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


def read_settings():
    """...
    """
    return WiFiSettings('DE', 'Downunder', 'Dragon76012__burgerZ*((-')


def enable(wifi_settings):
    """...
    """
    try:
        return subprocess.Popen([
            'sudo', '/opt/tinypilot-privileged/scripts/enable-wifi',
            wifi_settings.country_code, wifi_settings.ssid, wifi_settings.psk
        ])
    except subprocess.CalledProcessError as e:
        raise WifiApplyError(str(e.output).strip()) from e


def disable():
    """...
    """
    try:
        return subprocess.Popen([
            'sudo', '/opt/tinypilot-privileged/scripts/disable-wifi',
        ])
    except subprocess.CalledProcessError as e:
        raise WifiApplyError(str(e.output).strip()) from e
