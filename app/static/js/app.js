"use strict";

import { isAltGraphPressed, findKeyCode } from "./keycodes.js";
import * as settings from "./settings.js";

const socket = io();
let connectedToServer = false;

const screenCursorOptions = [
  "disabled", // To show on disconnect
  "default", // Note that this is the browser default, not TinyPilot's default.
  "none",
  "crosshair",
  "dot",
  "pointer",
  "cell",
];

// A map of keycodes to booleans indicating whether the key is currently pressed.
let keyState = {};

function hideElementById(id) {
  document.getElementById(id).style.display = "none";
}

function showElementById(id, display = "block") {
  document.getElementById(id).style.display = display;
}

// Limit display of recent keys to the last N keys, where limit = N.
function limitRecentKeys(limit) {
  const recentKeysDiv = document.getElementById("recent-keys");
  while (recentKeysDiv.childElementCount > limit) {
    recentKeysDiv.removeChild(recentKeysDiv.firstChild);
  }
}

function addKeyCard(key) {
  if (!settings.isKeyHistoryEnabled()) {
    return null;
  }
  const card = document.createElement("div");
  card.classList.add("key-card");
  let keyLabel = key;
  if (key === " ") {
    keyLabel = "Space";
  }
  card.style.fontSize = `${1.1 - 0.08 * keyLabel.length}em`;
  card.innerText = keyLabel;
  document.getElementById("recent-keys").appendChild(card);
  limitRecentKeys(10);
  return card;
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

function recalculateMouseEventThrottle(
  currentThrottle,
  lastRtt,
  lastWriteSucceeded
) {
  const maxThrottleInMilliseconds = 2000;
  if (!lastWriteSucceeded) {
    // Apply a 500 ms penalty to the throttle every time an event fails.
    return Math.min(currentThrottle + 500, maxThrottleInMilliseconds);
  }
  // Assume that the server can process messages in roughly half the round trip
  // time between an event message and its response.
  const roughSendTime = lastRtt / 2;

  // Set the new throttle to a weighted average between the last throttle time
  // and the last send time, with a 2/3 bias toward the last send time.
  const newThrottle = (roughSendTime * 2 + currentThrottle) / 3;
  return Math.min(newThrottle, maxThrottleInMilliseconds);
}

function unixTime() {
  return new Date().getTime();
}

function browserLanguage() {
  if (navigator.languages) {
    return navigator.languages[0];
  }
  return navigator.language || navigator.userLanguage;
}

// Send a keystroke message to the backend, and add a key card to the web UI.
function sendKeystroke(keystroke) {
  // On Android, when the user is typing with autocomplete enabled, the browser
  // sends dummy keydown events with a keycode of 229. Ignore these events, as
  // there's no way to map it to a real key.
  if (keystroke.keyCode === 229) {
    return;
  }
  let keyCard = undefined;
  if (!keystroke.metaKey) {
    keyCard = addKeyCard(keystroke.key);
  }
  socket.emit("keystroke", keystroke, (result) => {
    if (keyCard) {
      if (result.success) {
        keyCard.classList.add("processed-key-card");
      } else {
        keyCard.classList.add("unsupported-key-card");
      }
    }
  });
}

function onSocketConnect() {
  if (document.getElementById("shutdown-wait").show) {
    location.reload();
  } else {
    connectedToServer = true;
    document.getElementById("connection-indicator").connected = true;
    setCursor(settings.getScreenCursor());
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

function sendMouseEvent(buttons, relativeX, relativeY, vwheel, hwheel) {
  if (!connectedToServer) {
    return;
  }
  const remoteScreen = document.getElementById("remote-screen");
  const requestStartTime = unixTime();
  socket.emit(
    "mouse-event",
    {
      buttons,
      relativeX,
      relativeY,
      vwheel,
      hwheel,
    },
    (response) => {
      const requestEndTime = unixTime();
      const requestRtt = requestEndTime - requestStartTime;
      remoteScreen.millisecondsBetweenMouseEvents = recalculateMouseEventThrottle(
        remoteScreen.millisecondsBetweenMouseEvents,
        requestRtt,
        response.success
      );
    }
  );
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

function onModifierKeyButtonDoubleClick(evt) {
  const keyMappings = {
    "ctrl-modifier": {
      key: "Control",
      keyCode: 17,
    },
    "alt-modifier": {
      key: "Alt",
      keyCode: 18,
    },
    "shift-modifier": {
      key: "Shift",
      keyCode: 16,
    },
    "meta-modifier": {
      key: "Meta",
      keyCode: 91,
    },
    "sysrq-modifier": {
      key: "SysRq",
      keyCode: 44,
    },
  };

  if (!(evt.target.id in keyMappings)) {
    return;
  }
  const mapping = keyMappings[evt.target.id];

  sendKeystroke({
    metaKey:
      mapping.key === "Meta" ||
      document.getElementById("meta-modifier").pressed,
    altKey:
      mapping.key === "Alt" || document.getElementById("alt-modifier").pressed,
    shiftKey:
      mapping.key === "Shift" ||
      document.getElementById("shift-modifier").pressed,
    ctrlKey:
      mapping.key === "Control" ||
      document.getElementById("ctrl-modifier").pressed,
    altGraphKey: isAltGraphPressed(browserLanguage(), evt.keyCode, evt.key),
    sysrqKey:
      mapping.key === "SysRq" ||
      document.getElementById("sysrq-modifier").pressed,
    key: mapping.key,
    keyCode: mapping.keyCode,
    location: document.getElementById("left-right-toggle").modifierLocation,
  });
  socket.emit("keyRelease");
  clearManualModifiers();
}

function onDisplayHistoryChanged(evt) {
  if (evt.target.checked) {
    document.getElementById("recent-keys").classList.remove("hide-keys");
    settings.enableKeyHistory();
  } else {
    document.getElementById("recent-keys").classList.add("hide-keys");
    limitRecentKeys(0);
    settings.disableKeyHistory();
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
      metaKey: false,
      altKey: false,
      shiftKey: requiresShiftKey.test(textInput[i]),
      ctrlKey: false,
      altGraphKey: false,
      sysrqKey: false,
      key: key,
      keyCode: keyCode,
      location: null,
    });
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
    settings.setScreenCursor(cursor);
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
      evt.detail.relativeY,
      evt.detail.vwheel,
      evt.detail.hwheel
    );
  });
const displayHistoryCheckbox = document.getElementById(
  "display-history-checkbox"
);
displayHistoryCheckbox.addEventListener("change", onDisplayHistoryChanged);
displayHistoryCheckbox.checked = settings.isKeyHistoryEnabled();
if (!settings.isKeyHistoryEnabled()) {
  document.getElementById("recent-keys").classList.add("hide-keys");
}
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

for (const modifierKey of document.getElementsByTagName("modifier-key")) {
  modifierKey.addEventListener("dblclick", onModifierKeyButtonDoubleClick);
}

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
  if (cursorOption === settings.getScreenCursor()) {
    listItem.classList.add("nav-selected");
  }
  cursorList.appendChild(listItem);
}
socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
