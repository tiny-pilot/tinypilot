/**
 * Figure out the new URL under which TinyPilot will become
 * available after rebooting.
 * @param {Location} currentLocation
 * @param {string} oldHostname
 * @param {string} newHostname
 * @returns {string}
 */
export function determineFutureLocation(
  currentLocation,
  oldHostname,
  newHostname
) {
  const protocol = currentLocation.protocol + "//";
  let fqdn = currentLocation.hostname;
  if (fqdn.startsWith(oldHostname + ".")) {
    // When the fqdn (fully qualified domain name) starts with the old
    // hostname followed by a dot, then we replace the old one by the
    // new one in order to preserve the domain part.
    // E.g.: "oldtinypilot.home.local" => "newtinypilot.home.local"
    fqdn = fqdn.replace(oldHostname, newHostname);
  } else {
    // Otherwise we just assume the new hostname to be a fully qualified
    // one. That might not be correct, but it’s the best possible guess.
    fqdn = newHostname;
  }
  const port = currentLocation.port === "" ? "" : `:${currentLocation.port}`;
  return protocol + fqdn + port;
}
