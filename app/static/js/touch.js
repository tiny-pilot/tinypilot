/**
 * Adapter class that transforms touch events into synthetic mouse events.
 *
 * The idea behind having an adapter class like this is to stash away the touch
 * handling logic as good as possible, and to keep the complexity away from the
 * “regular” mouse handling code in the remote screen component.
 *
 * We currently only provide basic support for touch devices. So for now, this
 * adapter can emulate the following mouse actions:
 *   - Single left click
 *   - Double left click
 */
export class TouchToMouseAdapter {
  _lastTouchInfo = {
    timestamp: new Date(),
    clientX: 0,
    clientY: 0,
  };

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
    const touchInfo = {
      timestamp: new Date(),
      clientX: evt.touches[0].clientX,
      clientY: evt.touches[0].clientY,
    };

    // If this touch was a double click, use the mouse coordinates from the
    // previous touch, so that the position is exactly the same. (See comment
    // of `isDoubleClick` for why this is important.)
    if (isDoubleClick(touchInfo, this._lastTouchInfo)) {
      touchInfo.clientX = this._lastTouchInfo.clientX;
      touchInfo.clientY = this._lastTouchInfo.clientY;
    }

    this._lastTouchInfo = touchInfo;
    return mouseClickEvent(evt.target, this._lastTouchInfo, 1);
  }

  /**
   * @param {TouchEvent} evt - See:
   *     - https://developer.mozilla.org/en-US/docs/Web/API/TouchEvent
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchend_event
   *     - https://developer.mozilla.org/en-US/docs/Web/API/Element/touchcancel_event
   * @returns {SyntheticMouseEvent}
   */
  fromTouchEndOrCancel(evt) {
    // A `touchend` or `touchcancel` event doesn’t have the touches attribute
    // set, so we have to use the last known touch position instead, to keep
    // the mouse cursor in the same position.
    return mouseClickEvent(evt.target, this._lastTouchInfo, 0);
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

/**
 * Checks whether two consecutive touches are intended to be a double click
 * (double tap). This is true if both touches occur within a short time span,
 * and if their location is close to each other. Note that in contrast to a
 * mouse device, tapping twice on a touch screen almost never yields the exact
 * same position for both touches, in which case the target operating system
 * might not recognize the two clicks as proper double click.
 */
function isDoubleClick(touchInfo1, touchInfo2) {
  return (
    distancePx(touchInfo1, touchInfo2) < 50 &&
    delayMs(touchInfo1.timestamp, touchInfo2.timestamp) < 500
  );
}

function distancePx(touchInfo1, touchInfo2) {
  const a = Math.abs(touchInfo1.clientX - touchInfo2.clientX);
  const b = Math.abs(touchInfo1.clientY - touchInfo2.clientY);
  return Math.hypot(a, b);
}

function delayMs(date1, date2) {
  return Math.abs(date1.getTime() - date2.getTime());
}
