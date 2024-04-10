/**
 * Adapter class to transform touch events into mouse events, including all
 * properties as required by the `RateLimitedMouse` class.
 *
 * This adapter is currently only capable of emulating single left clicks.
 */
export class TouchToMouseAdapter {
  _lastTouchPosition = { clientX: 0, clientY: 0 };

  /**
   * @param {TouchEvent} evt See:
   *     - https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchstart_event
   * @returns {object}
   */
  fromTouchStart(evt) {
    // The corresponding `touchend` event won’t have the `touches` property
    // set, so we need to preserve the latest one to be able to reconstruct the
    // cursor position then.
    this._lastTouchPosition = evt.touches[0];
    return this._convert(evt, evt.touches[0], 1);
  }

  /**
   * @param {TouchEvent} evt
   *     - https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchend_event
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchcancel_event
   * @returns {object}
   */
  fromTouchEndOrCancel(evt) {
    return this._convert(evt, this._lastTouchPosition, 0);
  }

  _convert(evt, touchPosition, buttons) {
    evt.preventDefault();
    return {
      target: evt.target,
      clientX: touchPosition.clientX,
      clientY: touchPosition.clientY,
      buttons,
    };
  }
}
