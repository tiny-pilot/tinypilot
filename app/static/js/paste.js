pasteOverlay = document.getElementById("paste-overlay");
pasteOverlay.addEventListener("keydown", onPasteOverlayKeyDown);
pasteOverlay.addEventListener("paste", onPaste);
pasteOverlay.addEventListener("click", () => {
  hidePasteOverlay();
});

function isPasteOverlayShowing() {
  return pasteOverlay.getAttribute("show") === "true";
}

function showPasteOverlay() {
  pasteOverlay.setAttribute("show", "true");
  placeCaretInPasteOverlay();
}

function hidePasteOverlay() {
  pasteOverlay.setAttribute("show", "false");
}

function onPasteOverlayKeyDown(evt) {
  evt.stopPropagation();
  const ctrlKeyCode = 17;
  const vKeyCode = 86;
  // Return false on Ctrl or V because otherwise we capture the
  // event before the paste event can occur.
  if (evt.keyCode === ctrlKeyCode || evt.keyCode === vKeyCode) {
    return false;
  }
  // Treat any other key as cancellation of the paste.
  hidePasteOverlay();

  // Return control to normal input.
  document.getElementById("app").focus();
}

// Place the caret (cursor) in the paste div so that we can listen for paste
// events.
function placeCaretInPasteOverlay() {
  // This is largely copy-pasted from
  // https://stackoverflow.com/questions/4233265
  pasteOverlay.focus();

  // Move cursor to the end of the text.
  const range = document.createRange();
  range.selectNodeContents(pasteOverlay);
  range.collapse(false);
  const sel = window.getSelection();
  sel.removeAllRanges();
  sel.addRange(range);
}

function onPaste(evt) {
  // Stop data actually being pasted into div
  evt.stopPropagation();
  evt.preventDefault();

  // Get pasted data via clipboard API
  const clipboardData = evt.clipboardData || window.clipboardData;
  pasteOverlay.dispatchEvent(
    new CustomEvent("paste-text", {
      detail: clipboardData.getData("Text"),
      bubbles: true,
      composed: true,
    })
  );
  hidePasteOverlay();
}
