"use strict";

const socket = io();
let connectedToServer = false;
let keystrokeId = 0;

const screenCursorOptions = [
  "disabled", //to show on disconnect
  "default", // Note that this is the browser default, not TinyPilot's default.
  "none",
  "crosshair",
  "dot",
  "pointer",
  "cell",
];
const initialScreenCursor = "crosshair";
var settings = {
  cursor: initialScreenCursor,
};

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
  ]) {
    hideElementById(elementId);
  }
  const shutdownWait = document.getElementById("shutdown-wait");
  if (restart) {
    shutdownWait.message = "Restarting TinyPilot Device...";
  } else {
    shutdownWait.message = "Shutting down TinyPilot Device...";
    setTimeout(() => {
      const shutdownWait = document.getElementById("shutdown-wait");
      if (shutdownWait.show) {
        shutdownWait.message = "Shutdown complete";
        shutdownWait.hideSpinner();
      }
    }, 30 * 1000);
  }
  document.getElementById("shutdown-dialog").show = false;
  document.getElementById("shutdown-wait").show = true;
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

function browserLanguage() {
  if (navigator.languages) {
    return navigator.languages[0];
  }
  return navigator.language || navigator.userLanguage;
}

// Send a keystroke message to the backend, and add a key card to the web UI.
function sendKeystroke(keystroke) {
  //Ignore if keyCode is 229 (mobile)
  if (keystroke.keyCode === 229) {
    return;
  }
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
  if (document.getElementById("shutdown-wait").show) {
    location.reload();
  } else {
    connectedToServer = true;
    document.getElementById("connection-indicator").connected = true;
    restoreCursor();
  }
}

function onSocketDisconnect(reason) {
  setCursor("disabled", false);
  connectedToServer = false;
  const connectionIndicator = document.getElementById("connection-indicator");
  connectionIndicator.connected = false;
  connectionIndicator.disconnectReason = reason;
  document.getElementById("app").focus();
}

function onKeyDown(evt) {
  if (isPasteOverlayShowing()) {
    return;
  }
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
    altGraphKey: isAltGraphPressed(browserLanguage(), evt.keyCode, evt.key),
    sysrqKey: document.getElementById("sysrq-modifier").pressed,
    key: evt.key,
    keyCode: evt.keyCode,
    location: location,
  });
  clearManualModifiers();
}

function sendMouseEvent(buttons, relativeX, relativeY) {
  if (!connectedToServer) {
    return;
  }
  socket.emit("mouse-event", {
    buttons,
    relativeX,
    relativeY,
  });
}

function onKeyUp(evt) {
  if (isPasteOverlayShowing()) {
    return;
  }
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

function sendTextInput(textInput) {
  const language = browserLanguage();
  for (let i = 0; i < textInput.length; i++) {
    let key = textInput[i];
    // Ignore carriage returns.
    if (key === "\r") {
      continue;
    }
    const keyCode = findKeyCode([textInput[i].toLowerCase()], language);
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
      shiftKey: requiresShiftKey.test(textInput[i]),
      ctrlKey: false,
      altGraphKey: false,
      sysrqKey: false,
      key: key,
      keyCode: keyCode,
      keystrokeId: keystrokeId,
      location: null,
    });
  }
}

function restoreCursor() {
  if (
    "settings" in window &&
    "cursor" in window.settings &&
    window.settings.cursor != null
  ) {
    setCursor(window.settings.cursor);
  } else {
    setCursor(initialScreenCursor);
  }
}

function setCursor(cursor, save = true) {
  // Ensure the correct cursor option displays as active in the navbar.
  if (save) {
    for (const cursorListItem of document.querySelectorAll("#cursor-list li")) {
      if (cursor === cursorListItem.getAttribute("cursor")) {
        cursorListItem.classList.add("nav-selected");
      } else {
        cursorListItem.classList.remove("nav-selected");
      }
    }
    window.settings.cursor = cursor;
  }
  if (connectedToServer) {
    document.getElementById("remote-screen").cursor = cursor;
  }
}

document.onload = document.getElementById("app").focus();

document.addEventListener("keydown", onKeyDown);
document.addEventListener("keyup", onKeyUp);

document
  .getElementById("remote-screen")
  .addEventListener("mouse-event", (evt) => {
    sendMouseEvent(
      evt.detail.buttons,
      evt.detail.relativeX,
      evt.detail.relativeY
    );
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
document.getElementById("fullscreen-btn").addEventListener("click", (evt) => {
  document.getElementById("remote-screen").fullscreen = true;
  evt.preventDefault();
});
document.getElementById("paste-btn").addEventListener("click", () => {
  showPasteOverlay();
});

document
  .getElementById("paste-overlay")
  .addEventListener("paste-text", (evt) => {
    sendTextInput(evt.detail);

    // Give focus back to the app for normal text input.
    document.getElementById("app").focus();
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

// Add cursor options to navbar.
const cursorList = document.getElementById("cursor-list");
for (const cursorOption of screenCursorOptions.splice(1)) {
  const cursorLink = document.createElement("a");
  cursorLink.setAttribute("href", "#");
  cursorLink.innerText = cursorOption;
  cursorLink.addEventListener("click", (evt) => {
    setCursor(cursorOption);
    evt.preventDefault();
  });
  const listItem = document.createElement("li");
  listItem.appendChild(cursorLink);
  listItem.classList.add("cursor-option");
  listItem.setAttribute("cursor", cursorOption);
  if (cursorOption === initialScreenCursor) {
    listItem.classList.add("nav-selected");
  }
  cursorList.appendChild(listItem);
}
socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
socket.on("keystroke-received", (keystrokeResult) => {
  updateKeyStatus(keystrokeResult.keystrokeId, keystrokeResult.success);
});
