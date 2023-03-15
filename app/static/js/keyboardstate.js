import { isModifierCode, keystrokeToCanonicalCode } from "./keycodes.js";

const modifierPropToKeyCodesMapping = {
  altKey: ["AltLeft", "AltRight"],
  metaKey: ["MetaLeft", "MetaRight"],
  ctrlKey: ["ControlLeft", "ControlRight"],
  shiftKey: ["ShiftLeft", "ShiftRight"],
};

/**
 * KeyboardState keeps track of which buttons on the user's keyboard are
 * pressed. We can't rely on keyboard events (KeyboardEvent) alone because they
 * don't distinguish between left vs. right modifier keys. By tracking the full
 * keyboard state, we can send keystrokes to the remote system that more
 * faithfully match the buttons the user pressed in their browser.
 */
export class KeyboardState {
  constructor() {
    this._isKeyPressed = {};
  }

  /**
   * @param {string} canonicalCode - The canonical key code.
   * @returns {boolean}
   */
  isKeyPressed(canonicalCode) {
    return (
      canonicalCode in this._isKeyPressed && this._isKeyPressed[canonicalCode]
    );
  }

  /**
   * @param {KeyboardEvent} evt - https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  onKeyDown(evt) {
    const canonicalCode = keystrokeToCanonicalCode(evt);
    this._isKeyPressed[canonicalCode] = true;
    if (!isModifierCode(canonicalCode)) {
      this._fixInternalModifierStates(evt);
    }
  }

  /**
   * @param {KeyboardEvent} evt - https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  onKeyUp(evt) {
    const canonicalCode = keystrokeToCanonicalCode(evt);
    this._isKeyPressed[canonicalCode] = false;
  }

  /**
   * Fixes the internal modifiers’ state according to the information in the key
   * event. The internal state may have gotten out of sync in case the modifier
   * keys have been pressed or released while the browser window didn’t have
   * focus. The information in the event object takes precedence over this
   * class's cached state.
   * @param {KeyboardEvent} evt - https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  _fixInternalModifierStates(evt) {
    for (const [modifierProp, possibleCodes] of Object.entries(
      modifierPropToKeyCodesMapping
    )) {
      const isModifierPressed = evt[modifierProp];
      // In case the event reports the modifier to be released, we can just take
      // that over for the internal state.
      if (!isModifierPressed) {
        possibleCodes.forEach((c) => (this._isKeyPressed[c] = false));
      }

      // In case the event reports the modifier to be pressed, check whether the
      // the current internal state is in line with that. If not, adjust the
      // internal state; for the lack of information about left/right, we just
      // go for the left one as best guess.
      else if (
        isModifierPressed &&
        !possibleCodes.some((c) => this._isKeyPressed[c])
      ) {
        this._isKeyPressed[possibleCodes[0]] = true;
      }
    }
  }

  /**
   * @returns {string[]} An unordered array of canonical key codes.
   */
  getAllPressedModifierKeys() {
    return Object.entries(this._isKeyPressed)
      .filter(([keyCode, isPressed]) => isPressed && isModifierCode(keyCode))
      .map(([keyCode]) => keyCode);
  }
}
