"use strict";

const keyboardSocket = io();
let poweringDown = false;
let connectedToKeyboardService = false;
// The OS and browser capture some key combinations that involve modifier keys
// before they can reach JavaScript, so allow the user to set them manually.
let manualModifiers = {
  meta: false,
  alt: false,
  shift: false,
  ctrl: false,
};
let keystrokeId = 0;
const processingQueue = [];

// A map of keycodes to booleans indicating whether the key is currently pressed.
let keyState = {};

function hideElementById(id) {
  document.getElementById(id).style.display = "none";
}

function showElementById(id, display = "block") {
  document.getElementById(id).style.display = display;
}

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
  showElementById("error-panel");
}

function hideErrorIfType(errorType) {
  if (document.getElementById("error-type").innerText === errorType) {
    hideElementById("error-panel");
  }
}

function displayPoweringDownUI() {
  for (const elementId of [
    "error-panel",
    "remote-screen",
    "keystroke-history",
    "shutdown-confirmation-panel",
  ]) {
    hideElementById(elementId);
  }
  const shutdownMessage = document.createElement("h2");
  shutdownMessage.innerText = "Shutting down TinyPilot Device...";
  document.querySelector(".page-content").appendChild(shutdownMessage);
}

function getCsrfToken() {
  return document
    .querySelector("meta[name='csrf-token']")
    .getAttribute("content");
}

function shutdownDevice() {
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
      showError("Failed to Shut Down TinyPilot Device", error);
    });
}

function toggleManualModifier(modifier) {
  manualModifiers[modifier] = !manualModifiers[modifier];
}

function clearManualModifiers() {
  for (var modifier in manualModifiers) {
    manualModifiers[modifier] = false;
  }
  for (const button of document.getElementsByClassName("manual-modifier-btn")) {
    button.classList.remove("pressed");
    button.blur();
  }
}

function isModifierKeyCode(keyCode) {
  const modifierKeyCodes = [16, 17, 18, 91];
  return modifierKeyCodes.indexOf(keyCode) >= 0;
}

function isKeycodeAlreadyPressed(keyCode) {
  return keyCode in keyState && keyState[keyCode];
}

function isIgnoredKeystroke(keyCode) {
  // Ignore the keystroke if this is a modifier keycode and the modifier was
  // already pressed.
  return isModifierKeyCode(keyCode) && isKeycodeAlreadyPressed(keyCode);
}

function onKeyboardSocketConnect() {
  connectedToKeyboardService = true;
  showElementById("status-connected", "flex");
  hideElementById("status-disconnected");

  hideErrorIfType("Keyboard Connection Error");
}

function onKeyboardSocketDisconnect(reason) {
  connectedToKeyboardService = false;
  hideElementById("status-connected");
  showElementById("status-disconnected", "flex");

  // If user powered down the device, don't display an error message about
  // disconnecting from the keyboard service.
  if (poweringDown) {
    return;
  }
  showError("Keyboard Connection Error", reason);
}

function onKeyDown(evt) {
  if (!connectedToKeyboardService) {
    return;
  }
  if (isIgnoredKeystroke(evt.keyCode)) {
    return;
  }
  keyState[evt.keyCode] = true;
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

  keyboardSocket.emit("keystroke", {
    metaKey: evt.metaKey || manualModifiers.meta,
    altKey: evt.altKey || manualModifiers.alt,
    shiftKey: evt.shiftKey || manualModifiers.shift,
    ctrlKey: evt.ctrlKey || manualModifiers.ctrl,
    key: evt.key,
    keyCode: evt.keyCode,
    location: location,
  });
  clearManualModifiers();
}

function onKeyUp(evt) {
  keyState[evt.keyCode] = false;
}

function onManualModifierButtonClicked(evt) {
  toggleManualModifier(evt.target.getAttribute("modifier"));
  if (evt.target.classList.contains("pressed")) {
    evt.target.classList.remove("pressed");
  } else {
    evt.target.classList.add("pressed");
  }
}

function onDisplayHistoryChanged(evt) {
  if (evt.target.checked) {
    document.getElementById("recent-keys").style.visibility = "visible";
  } else {
    document.getElementById("recent-keys").style.visibility = "hidden";
    limitRecentKeys(0);
  }
}

document.querySelector("body").addEventListener("keydown", onKeyDown);
document.querySelector("body").addEventListener("keyup", onKeyUp);
document
  .getElementById("display-history-checkbox")
  .addEventListener("change", onDisplayHistoryChanged);
document.getElementById("power-btn").addEventListener("click", () => {
  showElementById("shutdown-confirmation-panel");
});
document.getElementById("hide-error-btn").addEventListener("click", () => {
  hideElementById("error-panel");
});
document
  .getElementById("confirm-shutdown")
  .addEventListener("click", shutdownDevice);
document.getElementById("cancel-shutdown").addEventListener("click", () => {
  hideElementById("shutdown-confirmation-panel");
});
for (const button of document.getElementsByClassName("manual-modifier-btn")) {
  button.addEventListener("click", onManualModifierButtonClicked);
}
keyboardSocket.on("connect", onKeyboardSocketConnect);
keyboardSocket.on("disconnect", onKeyboardSocketDisconnect);
keyboardSocket.on("keystroke-received", (data) => {
  updateKeyStatus(processingQueue.shift(), data.success);
});
