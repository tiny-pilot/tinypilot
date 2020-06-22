"use strict";

const socket = io();
let poweringDown = false;
let connectedToKeyboardService = false;
let keystrokeId = 0;
const processingQueue = [];

function limitRecentKeys(limit) {
  const recentKeysDiv = document.getElementById("recent-keys");
  while (recentKeysDiv.childElementCount > limit) {
    recentKeysDiv.removeChild(recentKeysDiv.firstChild);
  }
}

function addKeyCard(key, keystrokeId) {
  const card = document.createElement("div");
  card.classList.add("key-card");
  let keyLabel = key;
  if (key === " ") {
    keyLabel = "Space";
  }
  card.style.fontSize = `${1.1 - 0.08 * keyLabel.length}em`;
  card.innerText = keyLabel;
  card.setAttribute("keystroke-id", keystrokeId);
  document.getElementById("recent-keys").appendChild(card);
  limitRecentKeys(10);
}

function updateKeyStatus(keystrokeId, success) {
  const recentKeysDiv = document.getElementById("recent-keys");
  const cards = recentKeysDiv.children;
  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    if (parseInt(card.getAttribute("keystroke-id")) === keystrokeId) {
      if (success) {
        card.classList.add("processed-key-card");
      } else {
        card.classList.add("unsupported-key-card");
      }
      return;
    }
  }
}

function showError(errorType, errorMessage) {
  document.getElementById("error-type").innerText = errorType;
  document.getElementById("error-message").innerText = errorMessage;
  document.getElementById("error-panel").style.display = "block";
}

function displayPoweringDownUI() {
  for (const elementId of [
    "error-panel",
    "remote-screen",
    "keystroke-history",
  ]) {
    document.getElementById(elementId).style.display = "none";
  }
  const shutdownMessage = document.createElement("h2");
  shutdownMessage.innerText = "Shutting down KVM Pi Device...";
  document.querySelector(".page-content").appendChild(shutdownMessage);
}

function getCsrfToken() {
  return document
    .querySelector("meta[name='csrf-token']")
    .getAttribute("content");
}

function onSocketConnect() {
  connectedToKeyboardService = true;
  document.getElementById("status-connected").style.display = "flex";
  document.getElementById("status-disconnected").style.display = "none";
  document.getElementById("disconnect-reason").style.visibility = "hidden";
}

function onSocketDisconnect(reason) {
  connectedToKeyboardService = false;
  document.getElementById("status-connected").style.display = "none";
  document.getElementById("status-disconnected").style.display = "flex";

  // If user powered down the device, don't display an error message about
  // disconnecting from the keyboard service.
  if (poweringDown) {
    return;
  }
  document.getElementById("disconnect-reason").style.visibility = "visible";
  document.getElementById("disconnect-reason").innerText = "Error: " + reason;
}

function onKeyDown(evt) {
  if (!connectedToKeyboardService) {
    return;
  }
  if (!evt.metaKey) {
    evt.preventDefault();
    addKeyCard(evt.key, keystrokeId);
    processingQueue.push(keystrokeId);
    keystrokeId++;
  }

  let location = null;
  if (evt.location === 1) {
    location = "left";
  } else if (evt.location === 2) {
    location = "right";
  }

  socket.emit("keystroke", {
    metaKey: evt.metaKey,
    altKey: evt.altKey,
    shiftKey: evt.shiftKey,
    ctrlKey: evt.ctrlKey,
    key: evt.key,
    keyCode: evt.keyCode,
    location: location,
  });
}

function onDisplayHistoryChanged(evt) {
  if (evt.target.checked) {
    document.getElementById("recent-keys").style.visibility = "visible";
  } else {
    document.getElementById("recent-keys").style.visibility = "hidden";
    limitRecentKeys(0);
  }
}

function onPowerButtonClick() {
  fetch("/shutdown", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCsrfToken(),
    },
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  })
    .then((response) => {
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
      if (result.error) {
        return Promise.reject(new Error(result.error));
      }
      poweringDown = true;
      displayPoweringDownUI();
    })
    .catch((error) => {
      // Depending on timing, the server may not respond to the shutdown request
      // because it's shutting down. If we get a NetworkError, assume the
      // shutdown succeeded.
      if (error.message.indexOf("NetworkError") >= 0) {
        poweringDown = true;
        displayPoweringDownUI();
        return;
      }
      showError("Failed to Shut Down KVM Pi Device", error);
    });
}

document.querySelector("body").addEventListener("keydown", onKeyDown);
document
  .getElementById("display-history-checkbox")
  .addEventListener("change", onDisplayHistoryChanged);
document
  .getElementById("power-btn")
  .addEventListener("click", onPowerButtonClick);
document.getElementById("hide-error-btn").addEventListener("click", () => {
  document.getElementById("error-panel").style.display = "none";
});
socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
socket.on("keystroke-received", (data) => {
  updateKeyStatus(processingQueue.shift(), data.success);
});
