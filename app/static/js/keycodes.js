/**
 * @param {KeyboardEvent} keystroke - https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
 */
export function keystrokeToCanonicalCode(keystroke) {
  // Some keyboards send RightAlt/AltGraph as LeftControl then Alt, where the
  // Alt key has a blank code.
  if (keystroke.key === "Alt" && keystroke.code === "") {
    return "AltRight";
  }

  // Firefox calls it `OS...` instead of `Meta...`.
  if (keystroke.code === "OSLeft") {
    return "MetaLeft";
  }
  if (keystroke.code === "OSRight") {
    return "MetaRight";
  }

  return keystroke.code;
}

export function isModifierCode(code) {
  const modifierCodes = [
    "AltLeft",
    "AltRight",
    "ControlLeft",
    "ControlRight",
    "MetaLeft",
    "MetaRight",
    "ShiftLeft",
    "ShiftRight",
  ];
  return modifierCodes.indexOf(code) >= 0;
}
