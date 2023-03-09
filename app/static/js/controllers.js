function getCsrfToken(doc = document) {
  return getCsrfTokenElement(doc).getAttribute("content");
}

function getCsrfTokenElement(doc) {
  return doc.querySelector("meta[name='csrf-token']");
}

class ControllerError extends Error {
  /**
   * @param {string} details The original error message.
   * @param {string} [code] The error code, or `undefined` for non-application
   *     or unknown errors.
   */
  constructor(details, code) {
    super(details);
    this.code = code;
  }
}

/**
 * Processes response from the backend API.
 * @param {Object} response An object as returned by `fetch`
 * @returns {Promise<Object>}
 *     Success case: a JSON response with status 2xx. Promise resolves with
 *                   data from response body.
 *     Error case:   anything else, e.g. non-JSON or status 4xx/5xx.
 *                   Promise rejects with a `ControllerError`.
 *
 */
async function processJsonResponse(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    const status = `${response.status} ${response.statusText}`;
    const bodyText = await response.text();
    throw new ControllerError(
      "Malformed API response, content type must be JSON.\n" +
        `Response status: ${status}\n\n${bodyText}`
    );
  }

  let jsonBody;
  try {
    jsonBody = await response.json();
  } catch (jsonParseError) {
    throw new ControllerError(
      "Malformed API response, JSON body cannot be parsed.\n" + jsonParseError
    );
  }

  // Resolve on 2xx response:
  if (response.status >= 200 && response.status < 300) {
    return jsonBody;
  }
  // Reject otherwise:
  throw new ControllerError(
    jsonBody.message || "Unknown error: " + JSON.stringify(jsonBody),
    jsonBody.code
  );
}

export async function getLatestRelease() {
  let route = "/api/latestRelease";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then((updateInfo) => {
      ["version", "kind", "data"].forEach((field) => {
        if (!updateInfo.hasOwnProperty(field)) {
          throw new ControllerError(`Missing expected ${field} field`);
        }
      });
      return updateInfo;
    });
}

export async function getVersion() {
  let route = "/api/version";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then((versionResponse) => {
      if (!versionResponse.hasOwnProperty("version")) {
        throw new ControllerError("Missing expected version field");
      }
      return versionResponse;
    });
}

export async function shutdown(restart) {
  let route = "/api/shutdown";
  if (restart) {
    route = "/api/restart";
  }
  return fetch(route, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then((httpResponse) => {
      // A 502 usually means that nginx shutdown before it could process the
      // response. Treat this as success.
      if (httpResponse.status === 502) {
        return;
      }
      return processJsonResponse(httpResponse);
    })
    .catch((error) => {
      // Depending on timing, the server may not respond to the shutdown
      // request because it's shutting down. If we get a NetworkError, assume
      // the shutdown succeeded.
      if (error.message.indexOf("NetworkError") >= 0) {
        return;
      }
      throw error;
    });
}

export async function update() {
  let route = "/api/update";
  return fetch(route, {
    method: "PUT",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  }).then(processJsonResponse);
}

export async function getUpdateStatus() {
  let route = "/api/update";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then((data) => {
      if (!data.hasOwnProperty("status")) {
        throw new ControllerError("Missing expected status field");
      }
      if (!data.hasOwnProperty("updateError")) {
        throw new ControllerError("Missing expected updateError field");
      }
      return { status: data.status, updateError: data.updateError };
    });
}

export async function determineHostname() {
  const route = "/api/hostname";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then((hostnameResponse) => {
      if (!hostnameResponse.hasOwnProperty("hostname")) {
        throw new ControllerError("Missing expected hostname field");
      }
      return hostnameResponse.hostname;
    });
}

export async function changeHostname(newHostname) {
  const route = "/api/hostname";
  return fetch(route, {
    method: "PUT",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({ hostname: newHostname }),
  })
    .then(processJsonResponse)
    .then(() => newHostname);
}

export async function checkStatus(baseURL = "") {
  const route = "/api/status";
  return fetch(baseURL + route, {
    method: "GET",
    mode: "cors",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then(() => true);
}

export async function getDebugLogs() {
  return fetch("/api/debugLogs", {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then((response) => {
      if (!response.ok) {
        throw new ControllerError(response.statusText);
      }
      return response;
    })
    .then((response) => response.text());
}

export async function textToShareableUrl(text) {
  const baseUrl = "https://logs.tinypilotkvm.com";
  return fetch(baseUrl + "/", {
    method: "PUT",
    mode: "cors",
    cache: "no-cache",
    redirect: "error",
    body: text,
  })
    .then(processJsonResponse)
    .then((data) => {
      if (!data.hasOwnProperty("id")) {
        throw new ControllerError("Missing expected id field");
      }
      return data;
    })
    .then((data) => baseUrl + `/${data.id}`);
}

export async function getVideoSettings() {
  return fetch("/api/settings/video", {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then(processJsonResponse)
    .then((data) => {
      [
        "streamingMode",
        "frameRate",
        "defaultFrameRate",
        "mjpegQuality",
        "defaultMjpegQuality",
        "h264Bitrate",
        "defaultH264Bitrate",
      ].forEach((field) => {
        if (!data.hasOwnProperty(field)) {
          throw new ControllerError(`Missing expected ${field} field`);
        }
      });
      return data;
    });
}

export async function saveVideoSettings({
  streamingMode,
  frameRate,
  mjpegQuality,
  h264Bitrate,
}) {
  return fetch("/api/settings/video", {
    method: "PUT",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCsrfToken(),
    },
    body: JSON.stringify({
      streamingMode,
      frameRate,
      mjpegQuality,
      h264Bitrate,
    }),
  }).then(processJsonResponse);
}

export async function applyVideoSettings() {
  return fetch("/api/settings/video/apply", {
    method: "POST",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
  }).then(processJsonResponse);
}

export async function getLicensingMetadata() {
  return fetch("/licensing", {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  }).then(processJsonResponse);
}

export async function isMjpegStreamAvailable() {
  return fetch("/stream", {
    method: "HEAD",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then((response) => response.ok)
    .catch(() => false);
}
