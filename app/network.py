import dataclasses
import json
import logging
import re
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

_WIFI_COUNTRY_PATTERN = re.compile(r'^country\s+([A-Z]{2}):')
_INTERFACES_DIR = '/sys/class/net'


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
    """WiFi client connection settings.

    Attributes:
        country_code: 2-letter ISO 3166-1 alpha-2 regulatory country code.
            `None` when the regulatory domain is unset or unknown.
        ssid: WiFi network name. `None` when no WiFi client is configured.
        psk: WPA2-PSK passphrase. `None` for open networks. When reading
            existing settings, this is always `None` because stored credentials
            are never exposed back to callers.
    """
    country_code: str
    ssid: str
    psk: str


def get_network_interfaces():
    """Get a list of physical network interface names.

    Excludes loopback and virtual interfaces. A device is considered "physical"
    if /sys/class/net/<ifname>/device exists (i.e., it’s backed by hardware).

    Returns:
        A list of interface names for all available physical network interfaces.
    """
    sys_net_path = Path(_INTERFACES_DIR)
    if not sys_net_path.is_dir():
        logger.debug('%s is not available', str(_INTERFACES_DIR))
        return []

    interface_names = []
    for iface_path in sys_net_path.iterdir():
        # We know we don't want the loopback interface.
        if iface_path.name == 'lo':
            continue
        # If /sys/class/net/<ifname>/device exists, the interface appears
        # to be hardware.
        if (iface_path / 'device').exists():
            interface_names.append(iface_path.name)

    return sorted(interface_names)


def determine_network_status():
    """Checks the connectivity of the network interfaces.

    Returns:
        A list of InterfaceStatus objects for all available Ethernet and Wi-Fi
        network interfaces.
    """
    interfaces = get_network_interfaces()
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
        InterfaceStatus object.
    """
    status = InterfaceStatus(interface_name, False, None, None)

    try:
        # The command arguments are trusted because they aren't based on user
        # input.
        ip_cmd_out_raw = subprocess.check_output(  # noqa: S603
            [
                '/usr/bin/ip',
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
    """Determines the current WiFi client settings.

    Reads directly from NetworkManager via nmcli (unprivileged). Country code
    is read from the kernel regulatory domain via iw.

    Returns:
        WifiSettings object.
    """
    # Query SSID and mode from the tinypilot-wlan0 connection. nmcli exits
    # non-zero when the connection doesn't exist, which we treat as "no WiFi
    # configured".
    try:
        # The command arguments are trusted because they aren't based on user
        # input.
        props_output = subprocess.check_output(  # noqa: S603
            [
                '/usr/bin/nmcli', '--get-values',
                '802-11-wireless.mode,802-11-wireless.ssid', 'connection',
                'show', 'tinypilot-wlan0'
            ],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError:
        return WifiSettings(None, None, None)

    # nmcli returns empty output when the connection exists but isn't a wifi
    # connection, which we also treat as "no WiFi configured".
    try:
        mode, ssid = props_output.splitlines()
    except ValueError:
        return WifiSettings(None, None, None)

    # In AP mode, the SSID is the hotspot name, not a WiFi client setting.
    if mode != 'infrastructure':
        return WifiSettings(None, None, None)

    return WifiSettings(country_code=_read_wifi_country(), ssid=ssid, psk=None)


def _read_wifi_country():
    """Reads the WiFi regulatory country code from the kernel.

    Returns:
        The 2-letter country code, or None if not set or unreadable.
    """
    try:
        output = subprocess.check_output(  # noqa: S603
            ['/usr/sbin/iw', 'reg', 'get'],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError:
        return None

    for line in output.splitlines():
        match = _WIFI_COUNTRY_PATTERN.search(line)
        if match:
            country = match.group(1)
            # '00' means unset.
            if country == '00':
                return None
            return country
    return None


def enable_wifi(wifi_settings):
    """Enables a wireless network connection.

    Note: The function is executed in a "fire and forget" manner, to prevent
    the HTTP request from failing erratically due to a network interruption.

    Args:
        wifi_settings: The new, desired settings (of type WifiSettings)

    Raises:
        NetworkError
    """
    # The command arguments are trusted because the WiFi settings are validated
    # by the caller.
    args = [
        '/usr/bin/sudo', '/opt/tinypilot-privileged/scripts/enable-wifi',
        '--country', wifi_settings.country_code, '--ssid', wifi_settings.ssid
    ]
    try:
        # Ignore pylint since we're not managing the child process.
        # pylint: disable=consider-using-with
        if wifi_settings.psk:
            args.append('--psk')
            process = subprocess.Popen(  # noqa: S603
                args, stdin=subprocess.PIPE, text=True)
            process.communicate(input=wifi_settings.psk)
        else:
            subprocess.Popen(args)  # noqa: S603

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
            '/usr/bin/sudo',
            '/opt/tinypilot-privileged/scripts/disable-wifi',
        ])
    except subprocess.CalledProcessError as e:
        raise NetworkError(str(e.output).strip()) from e
