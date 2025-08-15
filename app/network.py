import dataclasses
import json
import logging
import os
import re
import subprocess

logger = logging.getLogger(__name__)

_WIFI_COUNTRY_PATTERN = re.compile(r'^\s*country=(.+)$')
_WIFI_SSID_PATTERN = re.compile(r'^\s*ssid="(.+)"$')


class Error(Exception):
    pass


class NetworkError(Error):
    pass


@dataclasses.dataclass
class InterfaceStatus:
    name: str
    is_connected: bool
    ip_address: str  # May be `None` if interface is disabled.
    mac_address: str  # May be `None` if interface is disabled.


@dataclasses.dataclass
class WifiSettings:
    country_code: str
    ssid: str
    psk: str  # Optional.


def _get_network_interfaces():
    """Get a list of physical network interface names.

    Excludes loopback and virtual interfaces. A device is considered "physical"
    if /sys/class/net/<if>/device exists (i.e., it’s backed by hardware).

    Returns:
        A list of interface names for all available physical network interfaces.
    """
    try:
        sys_net_path = '/sys/class/net'
        if not os.path.isdir(sys_net_path):
            logger.error('/sys/class/net is not available')
            return []

        names = []
        for ifname in os.listdir(sys_net_path):
            # We know we don't want loop out.
            if ifname == 'lo':
                continue
            # If /sys/class/net/<ifname>/device exists, the interface appears
            # to be hardware.
            if os.path.exists(os.path.join(sys_net_path, ifname, 'device')):
                names.append(ifname)

        return sorted(names)
    except Exception as e:
        logger.error('Failed to list interfaces from /sys/class/net: %s', e)
        return []


def determine_network_status():
    """Checks the connectivity of the network interfaces.

    Returns:
        A list of InterfaceStatus objects for all available Ethernet and Wi-Fi
        network interfaces.
    """
    interfaces = _get_network_interfaces()
    if not interfaces:
        return []

    return [inspect_interface(iface) for iface in interfaces]


def inspect_interface(interface_name):
    """Gathers information about a network interface.

    This method relies on the JSON output of the `ip` command. If the interface
    is available, the JSON structure is an array containing an object, which
    looks like the following (extra properties omitted for brevity):
        [{
            "operstate": "UP",
            "address": "e4:5f:01:98:65:05",
            "addr_info": [{"family":"inet", "local":"192.168.12.86"}]
        }]
    Note that `addr_info` might be empty, e.g. if `operstate` is `DOWN`;
    it also might contain additional families, such as `inet6` (IPv6).

    In general, we don’t have too much trust in the consistency of the JSON
    structure, as there is no reliable documentation for it. We try to handle
    and parse the output in a defensive and graceful way, to maximize
    robustness and avoid producing erratic failures.

    Args:
        interface_name: the technical interface name as string, e.g. `eth0`.

    Returns:
        InterfaceStatus object
    """
    status = InterfaceStatus(interface_name, False, None, None)

    try:
        ip_cmd_out_raw = subprocess.check_output([
            'ip',
            '-json',
            'address',
            'show',
            interface_name,
        ],
                                                 stderr=subprocess.STDOUT,
                                                 universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to run `ip` command: %s', str(e))
        return status

    try:
        json_output = json.loads(ip_cmd_out_raw)
    except json.decoder.JSONDecodeError as e:
        logger.error('Failed to parse JSON output of `ip` command: %s', str(e))
        return status

    if len(json_output) == 0:
        return status
    data = json_output[0]

    if 'operstate' in data:
        status.is_connected = data['operstate'] == 'UP'
    if 'address' in data:
        status.mac_address = data['address'].replace(':', '-')
    if 'addr_info' in data:
        status.ip_address = next((addr_info['local']
                                  for addr_info in data['addr_info']
                                  if addr_info['family'] == 'inet'), None)

    return status


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
    try:
        # Ignore pylint since we're not managing the child process.
        # pylint: disable=consider-using-with
        if wifi_settings.psk:
            args.append('--psk')
            process = subprocess.Popen(args, stdin=subprocess.PIPE, text=True)
            process.communicate(input=wifi_settings.psk)
        else:
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
