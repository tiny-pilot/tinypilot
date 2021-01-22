"use strict";

(function (windows) {
  // TODO: Avoid duplicating this function everywhere.
  function getCsrfToken() {
    return document
      .querySelector("meta[name='csrf-token']")
      .getAttribute("content");
  }

  function processResponse(response) {
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
  }

  function processResult(result) {
    if (result.hasOwnProperty("success") && result.success) {
      return result;
    }
    if (result.hasOwnProperty("error") && result.error) {
      return Promise.reject(new Error(result.error));
    }
    return Promise.reject(new Error("Unknown error"));
  }

  function getVersion() {
    let route = "/api/version";
    return fetch(route, {
      method: "GET",
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((response) => {
        processResponse(response);
        return response.json();
      })
      .then((result) => {
        return processResult(result);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  function getLatestRelease() {
    let route = "/api/latestRelease";
    return fetch(route, {
      method: "GET",
      mode: "same-origin",
      cache: "no-cache",
      redirect: "error",
    })
      .then((response) => {
        processResponse(response);
        return response.json();
      })
      .then((result) => {
        return processResult(result);
      })
      .catch((error) => {
        return Promise.reject(error);
      });
  }

  function update() {
    let route = "/api/update";
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
        processResponse(response);
        return response.json();
      })
      .then((result) => {
        return processResult(result);
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
  window.controllers.update = update;
})(window);
