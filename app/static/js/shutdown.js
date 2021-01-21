"use strict";
(function (windows) {
  // TODO: Avoid duplicating this function everywhere.
  function getCsrfToken() {
    return document
      .querySelector("meta[name='csrf-token']")
      .getAttribute("content");
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
      .then((response) => {
        // A 502 usually means that nginx shutdown before it could process the
        // response. Treat this as success.
        if (response.status === 502) {
          return Promise.resolve({});
        }
        if (response.status !== 200) {
          // See if the error response is JSON.
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.indexOf("application/json") !== -1) {
            return response.json().then((data) => {
              return Promise.reject(new Error(data.error));
            });
          }
          return Promise.reject(new Error(response.statusText));
        }
        return response.json();
      })
      .then((result) => {
        if (result.hasOwnProperty("success") && result.success) {
          return Promise.resolve({});
        }
        if (result.hasOwnProperty("error") && result.error) {
          return Promise.reject(new Error(result.error));
        }
        return Promise.reject(new Error("Unknown error"));
      })
      .catch((error) => {
        // Depending on timing, the server may not respond to the shutdown request
        // because it's shutting down. If we get a NetworkError, assume the
        // shutdown succeeded.
        if (error.message.indexOf("NetworkError") >= 0) {
          return Promise.resolve({});
        }
        return Promise.reject(error);
      });
  }

  if (!window.hasOwnProperty("controllers")) {
    window.controllers = {};
  }
  window.controllers.shutdown = shutdown;
})(window);
