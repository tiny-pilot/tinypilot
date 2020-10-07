let settings = {};
try {
  settings = JSON.parse(localStorage.getItem("settings"));
} catch {}

const defaults = {
  isKeyHistoryEnabled: true,
  cursor: "crosshair",
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

export function enableKeyHistory() {
  settings["isKeyHistoryEnabled"] = true;
  persistSettings();
}

export function disableKeyHistory() {
  settings["isKeyHistoryEnabled"] = false;
  persistSettings();
}

export function isKeyHistoryEnabled() {
  return settings["isKeyHistoryEnabled"];
}

export function getScreenCursor() {
  return settings["cursor"];
}

export function setScreenCursor(newCursor) {
  settings["cursor"] = newCursor;
  persistSettings();
}
