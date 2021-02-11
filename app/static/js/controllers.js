"use strict";

class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = "NetworkError";
  }
}

(function (windows) {
  function getCsrfToken() {
    return document
      .querySelector("meta[name='csrf-token']")
      .getAttribute("content");
  }

  // Reads a response from an HTTP endpoint that we expect to contain a JSON
  // body. Verifies the HTTP response was successful and the response type is
  // JSON, but doesn't check anything beyond that.
  function readHttpJsonResponse(response) {
    const contentType = response.headers.get("content-type");
    const isJson =
      contentType && contentType.indexOf("application/json") !== -1;

    // Success case is an HTTP 200 response and a JSON body.
    if (response.status === 200 && isJson) {
      return Promise.resolve(response.json());
    }

    // If this is JSON, try to read the error field.
    if (isJson) {
      return response.json().then((responseJson) => {
        if (responseJson.hasOwnProperty("error")) {
          return Promise.reject(new Error(responseJson.error));
        }
        return Promise.reject(new Error("Unknown error"));
      });
    }

    return response.text().then((text) => {
      if (text) {
        return Promise.reject(new Error(text));
      } else {
        return Promise.reject(new Error(response.statusText));
      }
    });
  }

  // Checks TinyPilot-level details of the response. The standard TinyPilot
  // response body contains two fields: "success" (bool) and "error" (string)
  // A message indicates success if success is true and error is non-null.
  function checkJsonSuccess(response) {
    if (response.hasOwnProperty("error") && response.error) {
      return Promise.reject(new Error(response.error));
    }
    if (!response.hasOwnProperty("success") || !response.success) {
      return Promise.reject(new Error("Unknown error"));
    }
    return Promise.resolve(response);
  }

  function getLatestRelease() {
    let route = "/api/latestRelease";
    return fetch(route, {
      method: "GET",
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((httpResponse) => {
        return readHttpJsonResponse(httpResponse);
      })
      .then((jsonResponse) => {
        return checkJsonSuccess(jsonResponse);
      })
      .then((versionResponse) => {
        if (!versionResponse.hasOwnProperty("version")) {
          return Promise.reject(new Error("Missing expected version field"));
        }
        return Promise.resolve({ version: versionResponse.version });
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  function getVersion() {
    let route = "/api/version";
    return fetch(route, {
      method: "GET",
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((httpResponse) => {
        return readHttpJsonResponse(httpResponse);
      })
      .then((jsonResponse) => {
        return checkJsonSuccess(jsonResponse);
      })
      .then((versionResponse) => {
        if (!versionResponse.hasOwnProperty("version")) {
          return Promise.reject(new Error("Missing expected version field"));
        }
        return Promise.resolve({ version: versionResponse.version });
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  function shutdown(restart) {
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
          return Promise.resolve({
            success: true,
            error: null,
          });
        }
        return readHttpJsonResponse(httpResponse);
      })
      .then((jsonResponse) => {
        return checkJsonSuccess(jsonResponse);
      })
      .then(() => {
        // The shutdown API has no details, so return an empty dict.
        return Promise.resolve({});
      })
      .catch((error) => {
        // Depending on timing, the server may not respond to the shutdown
        // request because it's shutting down. If we get a NetworkError, assume
        // the shutdown succeeded.
        if (error.message.indexOf("NetworkError") >= 0) {
          return Promise.resolve({});
        }
        return Promise.reject(error);
      });
  }

  function update() {
    let route = "/api/update";
    return fetch(route, {
      method: "PUT",
      headers: {
        "X-CSRFToken": getCsrfToken(),
      },
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((response) => {
        return readHttpJsonResponse(response);
      })
      .then((jsonResponse) => {
        return checkJsonSuccess(jsonResponse);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  function getUpdateStatus() {
    let route = "/api/update";
    return fetch(route, {
      method: "GET",
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((response) => {
        return readHttpJsonResponse(response);
      })
      .then((jsonResponse) => {
        return checkJsonSuccess(jsonResponse);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  if (!window.hasOwnProperty("controllers")) {
    window.controllers = {};
  }
  window.controllers.getVersion = getVersion;
  window.controllers.getLatestRelease = getLatestRelease;
  window.controllers.shutdown = shutdown;
  window.controllers.update = update;
  window.controllers.getUpdateStatus = getUpdateStatus;
})(window);
