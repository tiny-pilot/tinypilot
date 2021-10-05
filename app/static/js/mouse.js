/**
 * A mechanism to rate-limit mouse events so that they don't flood the network
 * channel or generate a long queue of stale events.
 *
 * Considerations:
 *  - Normal mouse movement can generate hundreds of mouse move events in a few
 *      seconds. Sending this many mouse events over the network can clog the
 *      network link or the server's emulated mouse USB interface.
 *  - We want to send mouse events in the same order they occurred to prevent
 *      unexpected behavior on the target system.
 *  - We want to send the first mouse event as quickly as possible to minimize
 *      latency when the user begins moving the mouse.
 *  - We never want to drop the last mouse movement in a sequence because it
 *      determines the mouse's final position. If we drop the final mouse event,
 *      the user might see an offset between their local cursor and their remote
 *      cursor.
 *  - We can drop some mouse events with a low probability of affecting the
 *      user's experience. For example, if the mouse moves in the following
 *      sequence:
 *
 *        t=0ms (0, 0)
 *        t=1ms (5, 5)
 *        t=2ms (10, 10)
 *
 *      The mouse event at t=1ms is mostly irrelevant because it doesn't matter
 *      to the user whether the mouse stopped at point (5, 5) on the way to
 *      (10, 10).
 *  - Some intermediate mouse events do affect user experience. Consider the
 *      following sequence:
 *
 *        t=0ms   (100, 100)
 *        t=20ms  (500, 100)
 *        t=100ms (100, 100)
 *
 *      The mouse ultimately lands in position (100, 100), but dropping the
 *      event at t=20ms might impact user experience if they meant to send a
 *      right-and-left gesture to the target computer.
 *  - We assume that mouse clicks and releases are high-priority. We should
 *      never drop a mouse click or release event.
 *  - Mouse wheel events have the same priority as mouse move events. It's okay
 *      to drop mouse wheel events if we're rate-limited.
 *  - The more mouse events we queue for transmission after a rate-limit window,
 *      the more latency the user will perceive because we're creating a backlog
 *      of mouse move events for the browser to process.
 *
 * Implementation:
 *  The current implementation fires mouse events immediately but maintains a
 *  timeout window to prevent any low-priority mouse events from firing until
 *  the timeout expires. If any low-priority mouse events occur within the
 *  timeout window, we save them to fire after the timeout window. We only queue
 *  a single event, so we drop all low-priority mouse events during the timeout
 *  window except for the final event.
 *
 *  We consider mouse click and release events to be high-priority and mouse
 *  move or wheel events to be low priority. We never drop high-priority events,
 *  and we send them immediately, ignoring the timeout window.
 */

export class RateLimitedMouse {
  /**
   * @param {number} millisecondsBetweenMouseEvents Number of milliseconds to
   * wait between sending low-priority mouse events to the backend.
   * @param {function(Object)} sendEventFn Function that sends parsed mouse
   * event to the backend server.
   */
  constructor(millisecondsBetweenMouseEvents, sendEventFn) {
    this.millisecondsBetweenMouseEvents = millisecondsBetweenMouseEvents;
    this._sendEventFn = sendEventFn;
    this._queuedEvent = null;
    this._eventTimer = null;
  }

  onMouseDown(evt) {
    // Treat mouse down events as high-priority. Clear the timeout window so
    // that we can process the mouse click immediately.
    this._clearTimeoutWindow();
    this._queueMouseEvent(evt);
  }

  onMouseUp(evt) {
    // Treat mouse up events as high-priority. Clear the timeout window so that
    // we can process the mouse click release immediately.
    this._clearTimeoutWindow();
    this._queueMouseEvent(evt);
  }

  onMouseMove(evt) {
    this._queueMouseEvent(evt);
  }

  onWheel(evt) {
    this._queueMouseEvent(evt);
  }

  _queueMouseEvent(evt) {
    this._queuedEvent = parseMouseEvent(evt);

    if (!this._isInTimeoutWindow()) {
      this._dequeueMouseEvent();
    }
  }

  _dequeueMouseEvent() {
    // If there are no events waiting, clear the timeout window.
    if (!this._queuedEvent) {
      this._clearTimeoutWindow();
      return;
    }

    this._sendEventFn(this._queuedEvent);
    this._queuedEvent = null;

    // Start a timer to process any new events that arrive during the timeout
    // window.
    this._eventTimer = setTimeout(() => {
      this._dequeueMouseEvent();
    }, this.millisecondsBetweenMouseEvents);
  }

  _isInTimeoutWindow() {
    return this._eventTimer === null;
  }

  _clearTimeoutWindow() {
    if (!this._isInTimeoutWindow()) {
      return;
    }

    clearTimeout(this._eventTimer);
    this._eventTimer = null;
  }
}

/**
 * Normalize mouse wheel delta to a value that's consistent across browsers.
 * Different browsers use different values for the delta, so we reduce it to a
 * simple -1, 0, or 1.
 *
 * @param {number} delta The mouse wheel delta value from the browser's mouse
 * event.
 * @returns {number} A value of -1, 0, or 1 representing whether the delta is
 * negative, zero, or positive, respectively.
 */
function normalizeWheelDelta(delta) {
  if (!delta) {
    return 0;
  }
  return Math.sign(delta);
}

/**
 * Parses a raw mouse event from the browser into a TinyPilot-specific object
 * containing information about the mouse event.
 *
 * @param {Object} evt A browser-generated event, such as mousedown or
 * mousemove.
 * @returns {Object} The mouse event data in TinyPilot-specific format with the
 * following properties:
 * - buttons (number) A bitmask representing which mouse buttons are pressed,
 *   in the same format as the buttons property from the browser's native mouse
 *   events.
 * - relativeX (number) A value between 0.0 and 1.0 representing the mouse's
 *   relative x-offset from the left edge of the screen.
 * - relativeY (number) A value between 0.0 and 1.0 representing the mouse's
 *   relative y-offset from the top edge of the screen.
 * - verticalWheelDelta (number) A -1, 0, or 1 representing movement of the
 *   mouse's vertical scroll wheel.
 * - horizontalWheelDelta (number) A -1, 0, or 1 representing movement of the
 *   mouse's horizontal scroll wheel.
 */
function parseMouseEvent(evt) {
  const boundingRect = evt.target.getBoundingClientRect();
  const cursorX = Math.max(0, evt.clientX - boundingRect.left);
  const cursorY = Math.max(0, evt.clientY - boundingRect.top);
  const width = boundingRect.right - boundingRect.left;
  const height = boundingRect.bottom - boundingRect.top;

  return {
    buttons: evt.buttons,
    relativeX: Math.min(1.0, Math.max(0.0, cursorX / width)),
    relativeY: Math.min(1.0, Math.max(0.0, cursorY / height)),
    // Negate y-delta so that negative number means scroll down.
    verticalWheelDelta: normalizeWheelDelta(evt.deltaY) * -1,
    horizontalWheelDelta: normalizeWheelDelta(evt.deltaX),
  };
}
