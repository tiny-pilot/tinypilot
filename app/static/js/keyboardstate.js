"use strict";

import { isModifierCode, keystrokeToCanonicalCode } from "./keycodes.js";

const modifierProp2KeyCodes = {
  altKey: ["AltLeft", "AltRight"],
  metaKey: ["MetaLeft", "MetaRight"],
  ctrlKey: ["CtrlLeft", "CtrlRight"],
  shiftKey: ["ShiftLeft", "ShiftRight"],
};

/**
 * This class is for keeping track internally of the keyboard state.
 */
export class KeyboardState {
  constructor() {
    this._keys = {};
  }

  /**
   * @param canonicalCode (string) The canonical key code.
   * @returns boolean
   */
  isKeyPressed(canonicalCode) {
    return canonicalCode in this._keys && this._keys[canonicalCode];
  }

  /**
   * @param evt https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  onKeyDown(evt) {
    const canonicalCode = keystrokeToCanonicalCode(evt);
    this._keys[canonicalCode] = true;
    if (!isModifierCode(canonicalCode)) {
      this._fixInternalModifierStates(evt);
    }
  }

  /**
   * @param evt https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  onKeyUp(evt) {
    const canonicalCode = keystrokeToCanonicalCode(evt);
    this._keys[canonicalCode] = false;
  }

  /**
   * Fixes the internal modifiers’ state according to the information in the key
   * event. The internal state may have gotten out of sync in case the modifier
   * keys have been pressed or released while the browser window didn’t have
   * focus. In doubt, the event object is authoritative.
   * @param evt https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent
   */
  _fixInternalModifierStates(evt) {
    for (const [modifierProp, possibleCodes] of Object.entries(
      modifierProp2KeyCodes
    )) {
      const isModifierPressed = evt[modifierProp];
      // In case the event reports the modifier to be released, we can just take
      // that over for the internal state.
      if (!isModifierPressed) {
        possibleCodes.forEach((c) => (this._keys[c] = false));
      }

      // In case the event reports the modifier to be pressed, check whether the
      // the current internal state is inline with that. If not, adjust the
      // internal state; for the lack of information about left/right, we just
      // go for the left one as best guess.
      else if (isModifierPressed && !possibleCodes.some((c) => this._keys[c])) {
        this._keys[possibleCodes[0]] = true;
      }
    }
  }
}
