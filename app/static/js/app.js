"use strict";

const socket = io();
let poweringDown = false;
let connectedToServer = false;
// The OS and browser capture some key combinations that involve modifier keys
// before they can reach JavaScript, so allow the user to set them manually.
let manualModifiers = {
  meta: false,
  alt: false,
  shift: false,
  ctrl: false,
  sysrq: false,
};
let keystrokeId = 0;
// To handle e.g. touch release events we need to know the last position sent
// to the server. Shape: { x: int, y: int }
let lastPosition = undefined;

// A map of keycodes to booleans indicating whether the key is currently pressed.
let keyState = {};

function hideElementById(id) {
  document.getElementById(id).style.display = "none";
}

function showElementById(id, display = "block") {
  document.getElementById(id).style.display = display;
}

function shouldDisplayKeyHistory() {
  return document.getElementById("recent-keys").style.visibility !== "hidden";
}

// Limit display of recent keys to the last N keys, where limit = N.
function limitRecentKeys(limit) {
  const recentKeysDiv = document.getElementById("recent-keys");
  while (recentKeysDiv.childElementCount > limit) {
    recentKeysDiv.removeChild(recentKeysDiv.firstChild);
  }
}

function addKeyCard(key, keystrokeId) {
  if (!shouldDisplayKeyHistory()) {
    return;
  }
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
  if (!shouldDisplayKeyHistory()) {
    return;
  }
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

function displayPoweringDownUI(restart) {
  for (const elementId of [
    "error-panel",
    "remote-screen",
    "keystroke-history",
    "shutdown-confirmation-panel",
  ]) {
    hideElementById(elementId);
  }
  const shutdownMessage = document.createElement("h2");
  if (restart) {
    shutdownMessage.innerText = "Restarting TinyPilot Device...";
  } else {
    shutdownMessage.innerText = "Shutting down TinyPilot Device...";
  }

  document.querySelector(".page-content").appendChild(shutdownMessage);
}

function getCsrfToken() {
  return document
    .querySelector("meta[name='csrf-token']")
    .getAttribute("content");
}

function sendShutdownRequest(restart) {
  let route = "/shutdown";
  if (restart) {
    route = "/restart";
  }
  fetch(route, {
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
      displayPoweringDownUI(restart);
    })
    .catch((error) => {
      // Depending on timing, the server may not respond to the shutdown request
      // because it's shutting down. If we get a NetworkError, assume the
      // shutdown succeeded.
      if (error.message.indexOf("NetworkError") >= 0) {
        poweringDown = true;
        displayPoweringDownUI(restart);
        return;
      }
      if (restart) {
        showError("Failed to restart TinyPilot device", error);
      } else {
        showError("Failed to shut down TinyPilot device", error);
      }
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
  const modifierKeyCodes = [16, 17, 18, 91, 84];
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

// Send a keystroke message to the backend, and add a key card to the web UI.
function sendKeystroke(keystroke) {
  if (!keystroke.metaKey) {
    addKeyCard(keystroke.key, keystroke.id);
  }
  socket.emit("keystroke", keystroke);
  if (!keystroke.metaKey) {
    // Increment the global keystroke ID.
    keystrokeId++;
  }
}

function onSocketConnect() {
  connectedToServer = true;
  showElementById("status-connected", "flex");
  hideElementById("status-disconnected");

  hideErrorIfType("Server Connection Error");
}

function onSocketDisconnect(reason) {
  connectedToServer = false;
  hideElementById("status-connected");
  showElementById("status-disconnected", "flex");

  // If user powered down the device, don't display an error message about
  // disconnecting from the keyboard service.
  if (poweringDown) {
    return;
  }
  showError("Server Connection Error", reason);
}

function onKeyDown(evt) {
  if (!connectedToServer) {
    return;
  }
  if (isIgnoredKeystroke(evt.keyCode)) {
    return;
  }
  keyState[evt.keyCode] = true;
  if (!evt.metaKey) {
    evt.preventDefault();
  }

  let location = null;
  if (evt.location === 1) {
    location = "left";
  } else if (evt.location === 2) {
    location = "right";
  }

  sendKeystroke({
    id: keystrokeId,
    metaKey: evt.metaKey || manualModifiers.meta,
    altKey: evt.altKey || manualModifiers.alt,
    shiftKey: evt.shiftKey || manualModifiers.shift,
    ctrlKey: evt.ctrlKey || manualModifiers.ctrl,
    sysrqKey: manualModifiers.sysrq,
    key: evt.key,
    keyCode: evt.keyCode,
    location: location,
  });
  clearManualModifiers();
}

function sendMouseEvent(evt) {  
  // Ensure that mouse drags don't attempt to drag the image on the screen.
  evt.preventDefault();

  emitMouseEvent(evt.target, evt, evt.buttons);
}

function sendTouchEvent(evt) {  
  // Ensure that mouse drags don't attempt to drag the image on the screen.
  evt.preventDefault();

  const touches = evt.touches;

  if (touches.length == 0 && lastPosition !== undefined) {
    // Release all mouse buttons
    socket.emit("mouse-event", {
      buttons: 0,
      relativeX: lastPosition.x,
      relativeY: lastPosition.y,
    });
    return;
  }

  const firstTouch = evt.touches[0];

  // Simulate a left mouse button event
  emitMouseEvent(evt.target, firstTouch, 1);
}

function emitMouseEvent(domTarget, position, buttons) {
  const boundingRect = domTarget.getBoundingClientRect();
  const cursorX = Math.max(0, position.clientX - boundingRect.left);
  const cursorY = Math.max(0, position.clientY - boundingRect.top);
  const width = boundingRect.right - boundingRect.left;
  const height = boundingRect.bottom - boundingRect.top;
  const relativeX = Math.min(1.0, Math.max(0.0, cursorX / width));
  const relativeY = Math.min(1.0, Math.max(0.0, cursorY / height));
  lastPosition = { x: relativeX, y: relativeY };
  socket.emit("mouse-event", {
    buttons: buttons,
    relativeX: relativeX,
    relativeY: relativeY,
  });
}

function onKeyUp(evt) {
  keyState[evt.keyCode] = false;
  if (!connectedToServer) {
    return;
  }
  if (isModifierKeyCode(evt.keyCode)) {
    socket.emit("keyRelease");
  }
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

// Forward all mouse activity that occurs over the image of the remote screen.
const screenImg = document.getElementById("remote-screen-img");
screenImg.addEventListener("mousemove", sendMouseEvent);
screenImg.addEventListener("mousedown", sendMouseEvent);
screenImg.addEventListener("mouseup", sendMouseEvent);
screenImg.addEventListener("touchmove", sendTouchEvent);
screenImg.addEventListener("touchstart", sendTouchEvent);
screenImg.addEventListener("touchend", sendTouchEvent);
// Ignore the context menu so that it doesn't block the screen when the user
// right-clicks.
screenImg.addEventListener("contextmenu", function (evt) {
  evt.preventDefault();
});
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
  .addEventListener("click", function () {
    sendShutdownRequest(/*restart=*/ false);
  });
document
  .getElementById("confirm-restart")
  .addEventListener("click", function () {
    sendShutdownRequest(/*restart=*/ true);
  });
document.getElementById("cancel-shutdown").addEventListener("click", () => {
  hideElementById("shutdown-confirmation-panel");
});
for (const button of document.getElementsByClassName("manual-modifier-btn")) {
  button.addEventListener("click", onManualModifierButtonClicked);
}
socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
socket.on("keystroke-received", (keystrokeResult) => {
  updateKeyStatus(keystrokeResult.keystrokeId, keystrokeResult.success);
});
