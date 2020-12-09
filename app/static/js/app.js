"use strict";

import { isModifierCode, findKeyCode, requiresShiftKey } from "./keycodes.js";
import { sendKeystroke } from "./keystrokes.js";
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

function showError(errorType, errorMessage) {
  document.getElementById("error-type").innerText = errorType;
  document.getElementById("error-message").innerText = errorMessage;
  showElementById("error-panel");
}

function displayPoweringDownUI(restart) {
  for (const elementId of ["error-panel", "remote-screen", "keystroke-panel"]) {
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

function isKeyPressed(code) {
  return code in keyState && keyState[code];
}

function isIgnoredKeystroke(code) {
  // Ignore the keystroke if this is a modifier keycode and the modifier was
  // already pressed. Otherwise, something like holding down the Shift key
  // is sent as multiple Shift key presses, which has special meaning on
  // certain OSes.
  return isModifierCode(code) && isKeyPressed(code);
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
function processKeystroke(keystroke) {
  // On Android, when the user is typing with autocomplete enabled, the browser
  // sends dummy keydown events with a keycode of 229. Ignore these events, as
  // there's no way to map it to a real key.
  if (keystroke.keyCode === 229) {
    resolve({});
  }
  const keyCard = document
    .querySelector("key-history")
    .addKeyCard(keystroke.key);
  const result = sendKeystroke(socket, keystroke);
  if (!keyCard) {
    return;
  }
  result
    .then(() => {
      keyCard.succeeded = true;
    })
    .catch(() => {
      keyCard.failed = true;
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

  code = evt.code;

  // Treat the AltGraph key like AltRight.
  if (key === "Alt" && evt.location === 1 && code === "") {
    code = "AltRight";
  }

  if (isIgnoredKeystroke(code)) {
    return;
  }

  keyState[code] = true;

  if (!connectedToServer) {
    return;
  }
  if (!evt.metaKey) {
    evt.preventDefault();
  }

  const onScreenKeyboard = document.getElementById("on-screen-keyboard");

  processKeystroke({
    metaKey: evt.metaKey || onScreenKeyboard.isMetaKeyPressed,
    altKey: evt.altKey || onScreenKeyboard.isAltKeyPressed,
    shiftKey: evt.shiftKey || onScreenKeyboard.isShiftKeyPressed,
    ctrlKey: evt.ctrlKey || onScreenKeyboard.isCtrlKeyPressed,
    altGraphKey:
      isKeyPressed("AltRight") || onScreenKeyboard.isRightAltKeyPressed,
    sysrqKey: onScreenKeyboard.isSysrqKeyPressed,
    key: evt.key,
    code: code,
  });
}

function sendMouseEvent(
  buttons,
  relativeX,
  relativeY,
  verticalWheelDelta,
  horizontalWheelDelta
) {
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
      verticalWheelDelta,
      horizontalWheelDelta,
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
  keyState[evt.code] = false;
  if (!connectedToServer) {
    return;
  }
  if (isModifierCode(evt.code)) {
    socket.emit("keyRelease");
  }
}

// Translate a single character into a keystroke and sends it to the backend.
function processTextCharacter(textCharacter, language) {
  // Ignore carriage returns.
  if (textCharacter === "\r") {
    return;
  }

  const code = findKeyCode([textCharacter.toLowerCase()], language);
  let friendlyName = textCharacter;
  // Give cleaner names to keys so that they render nicely in the history.
  if (textCharacter === "\n") {
    friendlyName = "Enter";
  } else if (textCharacter === "\t") {
    friendlyName = "Tab";
  }

  processKeystroke({
    metaKey: false,
    altKey: false,
    shiftKey: requiresShiftKey(textCharacter),
    ctrlKey: false,
    altGraphKey: false,
    sysrqKey: false,
    key: friendlyName,
    code: code,
  });
}

// Translate a string of text into individual keystrokes and sends them to the
// backend.
function processTextInput(textInput) {
  const language = browserLanguage();
  for (const textCharacter of textInput) {
    processTextCharacter(textCharacter, language);
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
      evt.detail.verticalWheelDelta,
      evt.detail.horizontalWheelDelta
    );
  });
document.getElementById("power-btn").addEventListener("click", () => {
  document.getElementById("shutdown-dialog").show = true;
});
document.getElementById("hide-error-btn").addEventListener("click", () => {
  hideElementById("error-panel");
});
for (const button of document.getElementsByClassName("manual-modifier-btn")) {
  button.addEventListener("click", onManualModifierButtonClicked);
}
document.getElementById("screenshot-btn").addEventListener("click", (evt) => {
  evt.target.download = "TinyPilot-" + new Date().toISOString() + ".jpg";
});
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
    processTextInput(evt.detail);

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

const keyHistory = document.querySelector("key-history");
keyHistory.show = settings.isKeyHistoryEnabled();
keyHistory.addEventListener("history-enabled", () => {
  settings.enableKeyHistory();
});
keyHistory.addEventListener("history-disabled", () => {
  settings.disableKeyHistory();
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
  if (cursorOption === settings.getScreenCursor()) {
    listItem.classList.add("nav-selected");
  }
  cursorList.appendChild(listItem);
}
socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
