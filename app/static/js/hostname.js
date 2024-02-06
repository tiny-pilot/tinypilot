/**
 * Determines the new base URL (i.e., the origin of the URL, without the
 * pathname or search parameters) of the TinyPilot device, given a new hostname.
 *
 * @example
 * // returns 'https://new-hostname.local'
 * determineFutureOrigin(
 *  new URL('https://old-hostname.local/some-path/'),
 *  'old-hostname',
 *  'new-hostname'
 * );
 *
 * @param {URL} currentLocation
 * @param {string} oldHostname
 * @param {string} newHostname
 * @returns {string}
 */
export function determineFutureOrigin(
  currentLocation,
  oldHostname,
  newHostname
) {
  const protocol = currentLocation.protocol + "//";
  let fqdn = currentLocation.hostname;
  if (oldHostname && fqdn.startsWith(oldHostname + ".")) {
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
