/**
 * Determines the parameters for redirecting the user after successful login.
 *
 * For issuing a page redirect on the call-side, the safest procedure is:
 *   1. Clone the `window.location` object into a new URL object.
 *   2. Assign the `pathname` and `search` properties individually.
 *   3. Feed the resulting URL object into e.g. `window.location.replace()`.
 *
 * @param {string|null} redirectQuery - The unencoded (!) value of the `redirect`
 *     query (search) parameter that the login page was opened with. This input
 *     argument may be `null`, to indicate that the `redirect` query parameter
 *     was absent.
 *     E.g.: /some-page?some=query-param
 * @returns {Object} - An object containing the redirect parameters in two
 *     properties `pathname` and `search` (both strings).
 *     E.g.: { pathname: "some-path", search: "?some=query-param" }
 */
export function determineRedirectParams(redirectQuery) {
  const baseRedirect = {
    pathname: "/",
    search: "",
  };

  if (!redirectQuery) {
    return baseRedirect;
  }

  // For security-reasons, we don’t accept if the leading slash is absent. We
  // also don’t accept a double leading slash, as that’s actually a
  // “same-scheme” absolute URL (e.g., `//www.google.com`).
  if (!redirectQuery.startsWith("/") || redirectQuery.startsWith("//")) {
    return baseRedirect;
  }

  return splitFullPath(redirectQuery);
}

function splitFullPath(fullPath) {
  const parts = fullPath.split("?");
  const pathname = parts[0];
  const search = parts.slice(1).join("?");
  return { pathname, search };
}
