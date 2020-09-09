"use strict";

const socket = io();
let connectedToServer = false;
let keystrokeId = 0;

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

function displayPoweringDownUI(restart) {
  for (const elementId of [
    "error-panel",
    "remote-screen",
    "keystroke-history",
    "shutdown-dialog",
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

function clearManualModifiers() {
  for (const modifierKey of document.getElementsByTagName("modifier-key")) {
    modifierKey.pressed = false;
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
  document.getElementById("connection-indicator").connected = true;
}

function onSocketDisconnect(reason) {
  connectedToServer = false;
  const connectionIndicator = document.getElementById("connection-indicator");
  connectionIndicator.connected = false;
  connectionIndicator.disconnectReason = reason;
  document.getElementById("app").focus();
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
    metaKey: evt.metaKey || document.getElementById("meta-modifier").pressed,
    altKey: evt.altKey || document.getElementById("alt-modifier").pressed,
    shiftKey: evt.shiftKey || document.getElementById("shift-modifier").pressed,
    ctrlKey: evt.ctrlKey || document.getElementById("ctrl-modifier").pressed,
    sysrqKey: document.getElementById("sysrq-modifier").pressed,
    key: evt.key,
    keyCode: evt.keyCode,
    location: location,
  });
  clearManualModifiers();
}

function sendMouseEvent(evt) {
  const boundingRect = evt.target.getBoundingClientRect();
  const cursorX = Math.max(0, evt.clientX - boundingRect.left);
  const cursorY = Math.max(0, evt.clientY - boundingRect.top);
  const width = boundingRect.right - boundingRect.left;
  const height = boundingRect.bottom - boundingRect.top;
  const relativeX = Math.min(1.0, Math.max(0.0, cursorX / width));
  const relativeY = Math.min(1.0, Math.max(0.0, cursorY / height));
  socket.emit("mouse-event", {
    buttons: evt.buttons,
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

function onDisplayHistoryChanged(evt) {
  if (evt.target.checked) {
    document.getElementById("recent-keys").style.visibility = "visible";
  } else {
    document.getElementById("recent-keys").style.visibility = "hidden";
    limitRecentKeys(0);
  }
}

function browserLanguage() {
  if (navigator.languages) {
    return navigator.languages[0];
  }
  return navigator.language || navigator.userLanguage;
}

function sendPastedText(pastedText) {
  const language = browserLanguage();
  for (let i = 0; i < pastedText.length; i++) {
    let key = pastedText[i];
    // Ignore carriage returns.
    if (key === "\r") {
      continue;
    }
    const keyCode = findKeyCode([pastedText[i].toLowerCase()], language);
    // Give cleaner names to keys so that they render nicely in the history.
    if (key === "\n") {
      key = "Enter";
    } else if (key === "\t") {
      key = "Tab";
    }
    // We need to identify keys which are typed with modifiers and send Shift +
    // the lowercase key.
    const requiresShiftKey = /^[A-Z¬!"£$%^&\*()_\+{}|<>\?:@~#]/;
    sendKeystroke({
      id: keystrokeId,
      metaKey: false,
      altKey: false,
      shiftKey: requiresShiftKey.test(pastedText[i]),
      ctrlKey: false,
      key: key,
      keyCode: keyCode,
      keystrokeId: keystrokeId,
      location: null,
    });
  }
  // Give focus back to the app for normal text input.
  document.getElementById("app").focus();
}

document.onload = document.getElementById("app").focus();

document.getElementById("app").addEventListener("keydown", onKeyDown);
document.getElementById("app").addEventListener("keyup", onKeyUp);

// Forward all mouse activity that occurs over the image of the remote screen.
const screenImg = document.getElementById("remote-screen-img");
screenImg.addEventListener("mousemove", function (evt) {
  // Ensure that mouse drags don't attempt to drag the image on the screen.
  evt.preventDefault();
  sendMouseEvent(evt);
});
screenImg.addEventListener("mousedown", sendMouseEvent);
screenImg.addEventListener("mouseup", sendMouseEvent);
// Ignore the context menu so that it doesn't block the screen when the user
// right-clicks.
screenImg.addEventListener("contextmenu", function (evt) {
  evt.preventDefault();
});
document
  .getElementById("display-history-checkbox")
  .addEventListener("change", onDisplayHistoryChanged);
document.getElementById("power-btn").addEventListener("click", () => {
  document.getElementById("shutdown-dialog").show = true;
});
document.getElementById("hide-error-btn").addEventListener("click", () => {
  hideElementById("error-panel");
});
for (const button of document.getElementsByClassName("manual-modifier-btn")) {
  button.addEventListener("click", onManualModifierButtonClicked);
}
document.getElementById("paste-btn").addEventListener("click", () => {
  document.getElementById("paste-overlay").show = true;
});
document
  .getElementById("paste-overlay")
  .addEventListener("paste-text", (evt) => {
    sendPastedText(evt.detail);
  });
document
  .getElementById("shutdown-dialog")
  .addEventListener("shutdown-started", (evt) => {
    displayPoweringDownUI(evt.detail.restart);
  });
document
  .getElementById("shutdown-dialog")
  .addEventListener("shutdown-failure", (evt) => {
    showError(evt.detail.summary, evt.detail.detail);
  });

socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
socket.on("keystroke-received", (keystrokeResult) => {
  updateKeyStatus(keystrokeResult.keystrokeId, keystrokeResult.success);
});
