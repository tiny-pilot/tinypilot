// This function is a duplicate from app.js hideElementById
function hideElementById(id) {
  document.getElementById(id).style.display = "none";
}

function completeUpdate(interval, updateWait) {
  clearInterval(interval);
  updateWait.timer = "";
  // Check if any error was emitted (the error-panel would show)
  const errorPanel = document.getElementById("error-panel");
  if (getComputedStyle(errorPanel).display === "none") {
    updateWait.message = "Update complete.";
    setTimeout(() => {
      updateWait.show = false;
    }, 2000);
    document.getElementById("shutdown-dialog").sendShutdownRequest(true);
  }
}

function startCountdownTimer(duration, updateWait) {
  let timer = duration,
    minutes,
    seconds;
  const interval = setInterval(() => {
    minutes = parseInt(timer / 60, 10);
    seconds = parseInt(timer % 60, 10);

    minutes = minutes < 10 ? "0" + minutes : minutes;
    seconds = seconds < 10 ? "0" + seconds : seconds;

    updateWait.timer = minutes + ":" + seconds;

    if (--timer < 0) {
      completeUpdate(interval, updateWait);
    }
  }, 1000);
}

export function getVersion() {
  let route = "/api/version";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  }).then((response) => {
    return response.json();
  });
}

export function getLatestRelease() {
  let route = "/api/latestRelease";
  return fetch(route, {
    method: "GET",
    mode: "same-origin",
    cache: "no-cache",
    redirect: "error",
  }).then((response) => {
    return response.json();
  });
}

export function displayUpdatingUI() {
  for (const elementId of ["error-panel", "remote-screen", "keystroke-panel"]) {
    hideElementById(elementId);
  }
  const updateWait = document.getElementById("update-wait");
  document.getElementById("update-dialog").show = false;

  updateWait.message = "Please wait while TinyPilot updates.";
  updateWait.show = true;

  const countdownDuration = 60 * 5;
  startCountdownTimer(countdownDuration, updateWait);
}
