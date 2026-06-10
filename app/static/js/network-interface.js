/**
 * Converts a network interface name to a user-friendly display name.
 * @param {string} networkInterfaceName - The name of the network interface.
 * @returns {string} The display name for the interface.
 */
export function getNetworkInterfaceDisplayName(networkInterfaceName) {
  if (!networkInterfaceName) {
    return "n/a";
  }
  // Match "eth" followed by one or more digits.
  if (/^eth\d+$/.test(networkInterfaceName)) {
    return `LAN${parseInt(networkInterfaceName.slice(3)) + 1}`;
  }
  // Match "wlan" followed by one or more digits.
  if (/^wlan\d+$/.test(networkInterfaceName)) {
    return "Wi-Fi";
  }
  return networkInterfaceName;
}
