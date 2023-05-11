let settings = {};
try {
  settings = JSON.parse(localStorage.getItem("settings"));
} catch {
  // Ignore errors.
}

const defaults = {
  isKeyHistoryEnabled: true,
  cursor: "default",
  isKeyboardVisible: true,
};

// Initialize any undefined settings to their default values.
if (!settings) {
  settings = {};
}
for (const [key, value] of Object.entries(defaults)) {
  if (!(key in settings)) {
    settings[key] = value;
  }
}

function persistSettings() {
  window.localStorage.setItem("settings", JSON.stringify(settings));
}

export function enableKeystrokeHistory() {
  settings["isKeyHistoryEnabled"] = true;
  persistSettings();
}

export function disableKeystrokeHistory() {
  settings["isKeyHistoryEnabled"] = false;
  persistSettings();
}

export function isKeystrokeHistoryEnabled() {
  return settings["isKeyHistoryEnabled"];
}

export function getScreenCursor() {
  return settings["cursor"];
}

export function setScreenCursor(newCursor) {
  settings["cursor"] = newCursor;
  persistSettings();
}

export function isKeyboardVisible() {
  return settings["isKeyboardVisible"];
}

export function setKeyboardVisibility(isVisible) {
  settings["isKeyboardVisible"] = isVisible;
  persistSettings();
}
