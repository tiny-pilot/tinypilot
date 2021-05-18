"use strict";

import {
  isModifierCode,
  findKeyCode,
  keystrokeToCanonicalCode,
  requiresShiftKey,
} from "./keycodes.js";
import { sendKeystroke } from "./keystrokes.js";
import * as settings from "./settings.js";
import { OverlayTracker } from "./overlays.js";

const socket = io();
let connectedToServer = false;

// A map of keycodes to booleans indicating whether the key is currently pressed.
let keyState = {};

// Keep track of overlays, in order to properly deactivate keypress forwarding.
const overlayTracker = new OverlayTracker();

function hideElementById(id) {
  document.getElementById(id).style.display = "none";
}

function showElementById(id, display = "block") {
  document.getElementById(id).style.display = display;
}

function isElementShown(id) {
  return document.getElementById(id).style.display !== "none";
}

/**
 * @see the `setup` method in error-dialog.html for the `errorInfo` param
 */
function showError(errorInfo) {
  console.error(`${errorInfo.title}:\n${errorInfo.details}`);
  document.getElementById("error-dialog").setup(errorInfo);
  document.getElementById("error-overlay").show();
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

const keystrokeHistory = document.getElementById("status-bar").keystrokeHistory;

// Send a keystroke message to the backend, and add a key card to the web UI.
function processKeystroke(keystroke) {
  // On Android, when the user is typing with autocomplete enabled, the browser
  // sends dummy keydown events with a keycode of 229. Ignore these events, as
  // there's no way to map it to a real key.
  if (keystroke.keyCode === 229) {
    resolve({});
  }
  const keystrokeHistoryEvent = keystrokeHistory.push(keystroke.key);
  const result = sendKeystroke(socket, keystroke);
  result
    .then(() => {
      keystrokeHistoryEvent.status = "succeeded";
    })
    .catch(() => {
      keystrokeHistoryEvent.status = "failed";
    });
}

function onSocketConnect() {
  if (document.getElementById("shutdown-overlay").isShown()) {
    location.reload();
    return;
  }

  connectedToServer = true;
  document.getElementById("status-bar").connectionIndicator.connected = true;
  setCursor(settings.getScreenCursor());
}

function onSocketDisconnect(reason) {
  setCursor("disabled", false);
  connectedToServer = false;
  const connectionIndicator = document.getElementById("status-bar")
    .connectionIndicator;
  connectionIndicator.connected = false;
  connectionIndicator.disconnectReason = reason;
  document.getElementById("app").focus();
}

function onKeyDown(evt) {
  if (isPasteOverlayShowing() || overlayTracker.hasOverlays()) {
    return;
  }

  const code = keystrokeToCanonicalCode(evt);

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
    altKey: evt.altKey || onScreenKeyboard.isLeftAltKeyPressed,
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
  const code = keystrokeToCanonicalCode(evt);
  keyState[code] = false;
  if (!connectedToServer) {
    return;
  }
  if (isModifierCode(code)) {
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
    document.getElementById("menu-bar").cursor = cursor;
    settings.setScreenCursor(cursor);
  }
  if (connectedToServer) {
    document.getElementById("remote-screen").cursor = cursor;
  }
}

function setKeyboardVisibility(isVisible) {
  if (isVisible) {
    showElementById("on-screen-keyboard");
  } else {
    hideElementById("on-screen-keyboard");
  }
  settings.setKeyboardVisibility(isVisible);
  document.getElementById("menu-bar").isKeyboardVisible = isVisible;
}

function setKeystrokeHistoryStatus(isEnabled) {
  if (isEnabled) {
    settings.enableKeystrokeHistory();
    document.getElementById("status-bar").keystrokeHistory.enable();
  } else {
    settings.disableKeystrokeHistory();
    document.getElementById("status-bar").keystrokeHistory.disable();
  }
  document.getElementById("menu-bar").isInputIndicatorEnabled = isEnabled;
}

document.onload = document.getElementById("app").focus();

document.addEventListener("keydown", onKeyDown);
document.addEventListener("keyup", onKeyUp);
document.addEventListener("overlay-toggled", (evt) => {
  overlayTracker.trackStatus(evt.target, evt.detail.isShown);
});

const menuBar = document.getElementById("menu-bar");
menuBar.cursor = settings.getScreenCursor();
menuBar.addEventListener("cursor-selected", (evt) => {
  setCursor(evt.detail.cursor);
});
menuBar.addEventListener("keystroke-history-toggled", () => {
  const isEnabled = document.getElementById("status-bar").keystrokeHistory
    .isEnabled;
  setKeystrokeHistoryStatus(!isEnabled);
});
menuBar.addEventListener("keyboard-visibility-toggled", () => {
  setKeyboardVisibility(!isElementShown("on-screen-keyboard"));
});
menuBar.addEventListener("shutdown-dialog-requested", () => {
  document.getElementById("shutdown-overlay").show();
});
menuBar.addEventListener("update-dialog-requested", () => {
  document.getElementById("update-overlay").show();
  document.getElementById("update-dialog").checkVersion();
});
menuBar.addEventListener("change-hostname-dialog-requested", () => {
  document.getElementById("change-hostname-overlay").show();
  document.getElementById("change-hostname-dialog").initialize();
});
menuBar.addEventListener("fullscreen-requested", () => {
  document.getElementById("remote-screen").fullscreen = true;
});
menuBar.addEventListener("debug-logs-dialog-requested", () => {
  document.getElementById("debug-dialog").getLogs();
  document.getElementById("debug-overlay").show();
});
menuBar.addEventListener("video-settings-dialog-requested", () => {
  document.getElementById("video-settings-dialog").getSettings();
  document.getElementById("video-settings-overlay").show();
});
menuBar.addEventListener("paste-requested", () => {
  showPasteOverlay();
});
setKeyboardVisibility(settings.isKeyboardVisible());
setKeystrokeHistoryStatus(settings.isKeystrokeHistoryEnabled());

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

const errorEvents = [
  "update-failure",
  "change-hostname-failure",
  "shutdown-failure",
  "video-settings-failure",
  "debug-logs-failure",
];
errorEvents.forEach((name) => {
  document.addEventListener(name, (evt) => {
    showError(evt.detail);
  });
});

document
  .getElementById("paste-overlay")
  .addEventListener("paste-text", (evt) => {
    processTextInput(evt.detail);

    // Give focus back to the app for normal text input.
    document.getElementById("app").focus();
  });
const shutdownDialog = document.getElementById("shutdown-dialog");
shutdownDialog.addEventListener("shutdown-started", (evt) => {
  // Hide the interactive elements of the page during shutdown.
  for (const elementId of ["remote-screen", "on-screen-keyboard"]) {
    hideElementById(elementId);
  }
});

socket.on("connect", onSocketConnect);
socket.on("disconnect", onSocketDisconnect);
