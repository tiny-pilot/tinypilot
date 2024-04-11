/**
 * Adapter class that transforms touch events into synthetic mouse events.
 *
 * The idea behind having an adapter class like this is to stash away the touch
 * handling logic as good as possible, and to keep the complexity away from the
 * “regular” mouse handling code in the remote screen component.
 *
 * We currently only provide rudimentary support for touch devices. So for now,
 * this adapter is only capable of emulating single left clicks.
 */
export class TouchToMouseAdapter {
  _lastTouchPosition = { clientX: 0, clientY: 0 };

  /**
   * Synthetic mouse event that includes all properties that the
   * `RateLimitedMouse.parseMouseEvent()` method relies on.
   * @typedef {Object} SyntheticMouseEvent
   */

  /**
   * @param {TouchEvent} evt - See:
   *     - https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchstart_event
   * @returns {SyntheticMouseEvent}
   */
  fromTouchStart(evt) {
    // The corresponding `touchend` event won’t have the `touches` property
    // set, so we need to preserve the latest one to be able to reconstruct the
    // cursor position for the touch/mouse release.
    this._lastTouchPosition = evt.touches[0];
    return mouseClickEvent(evt.target, evt.touches[0], 1);
  }

  /**
   * @param {TouchEvent} evt - See:
   *     - https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchend_event
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchcancel_event
   * @returns {SyntheticMouseEvent}
   */
  fromTouchEndOrCancel(evt) {
    return mouseClickEvent(evt.target, this._lastTouchPosition, 0);
  }
}

function mouseClickEvent(target, touchPosition, buttons) {
  return {
    target,
    buttons,
    clientX: touchPosition.clientX,
    clientY: touchPosition.clientY,
    deltaX: 0,
    deltaY: 0,
  };
}
