"use strict";

import * as settings from "./settings.js";
import { OverlayTracker } from "./overlays.js";

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

function setCursor(cursor, save = true) {
  // Ensure the correct cursor option displays as active in the navbar.
  if (save) {
    document.getElementById("menu-bar").cursor = cursor;
    settings.setScreenCursor(cursor);
  }
  document.getElementById("remote-screen").cursor = cursor;
}

document.onload = document.getElementById("app").focus();

document.addEventListener("overlay-toggled", (evt) => {
  overlayTracker.trackStatus(evt.target, evt.detail.isShown);
});

const menuBar = document.getElementById("menu-bar");
menuBar.cursor = settings.getScreenCursor();
menuBar.addEventListener("cursor-selected", (evt) => {
  setCursor(evt.detail.cursor);
});
menuBar.addEventListener("shutdown-dialog-requested", () => {
  document.getElementById("shutdown-overlay").show();
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

const errorEvents = [
  "update-failure",
  "change-hostname-failure",
  "shutdown-failure",
];
errorEvents.forEach((name) => {
  document.addEventListener(name, (evt) => {
    showError(evt.detail);
  });
});

const shutdownDialog = document.getElementById("shutdown-dialog");
shutdownDialog.addEventListener("shutdown-started", (evt) => {
  // Hide the interactive elements of the page during shutdown.
  for (const elementId of ["remote-screen"]) {
    hideElementById(elementId);
  }
});
