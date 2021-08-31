let csrfRefreshLock = null;

export function getCsrfToken(doc = document) {
  return getCsrfTokenElement(doc).getAttribute("content");
}

function getCsrfTokenElement(doc) {
  return doc.querySelector("meta[name='csrf-token']");
}

function setCsrfToken(tokenValue) {
  return getCsrfTokenElement(document).setAttribute("content", tokenValue);
}

async function refreshCsrfToken() {
  return fetch("/")
    .then(function (response) {
      return response.text();
    })
    .then(function (html) {
      const doc = new DOMParser().parseFromString(html, "text/html");
      const csrfToken = getCsrfToken(doc);
      setCsrfToken(csrfToken);
      return Promise.resolve();
    })
    .catch(function (error) {
      return Promise.reject("Failed to refresh CSRF token: " + error);
    });
}

/**
 * Adds retry functionality to the Fetch API.
 * If the HTTP request fails due to a stale CSRF token, then refresh the CSRF
 * token and retry the original request once more. This function has the same
 * API as the global fetch function.
 */
export async function fetchWithCsrfRetry(resource, init) {
  let response = await fetch(resource, init);
  // Only retry a request when the original request has a CSRF token header.
  // This is to avoid programmers from getting lazy and never including a CSRF
  // token header in their requests.
  let csrfTokenHeader = init?.headers?.["X-CSRFToken"] || null;
  if (!csrfTokenHeader) {
    console.error(
      "Cannot trigger a CSRF token refresh when the CSRF token header is missing from the request."
    );
    return response;
  }
  if (response.status !== 403) {
    return response;
  }
  if (!csrfRefreshLock) {
    // Initialize the lock.
    csrfRefreshLock = new Promise(async (resolve, reject) => {
      try {
        await refreshCsrfToken();
        resolve();
      } catch (e) {
        reject(e);
      } finally {
        // Release the lock.
        csrfRefreshLock = null;
      }
    });
  }
  // Wait for the CSRF token to be refreshed.
  await csrfRefreshLock;
  // Update the CSRF token header.
  init.headers["X-CSRFToken"] = getCsrfToken();
  // Retry the original request.
  return fetch(resource, init);
}
