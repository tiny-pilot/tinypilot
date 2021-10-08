/**
 * A mechanism to rate-limit mouse events so that they don't flood the network
 * channel or generate a long queue of stale events.
 *
 * The current implementation fires mouse events immediately but maintains a
 * timeout window to prevent any low-priority mouse events from firing until the
 * timeout expires. If any low-priority mouse events occur within the timeout
 * window, we save them to fire after the timeout window. We only queue a single
 * event, so we drop all low-priority mouse events during the timeout window
 * except for the final event. We never drop high-priority events - we send them
 * them immediately, discarding any previous timeout window and replacing it
 * with a fresh window.
 *
 * Here is how we classify the types of mouse events:
 *
 *    | Event type | Priority |
 *    |------------|----------|
 *    | Click      | High     |
 *    | Release    | High     |
 *    | Move       | Low      |
 *    | Wheel      | Low      |
 *
 * # Considerations
 *
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
 *
 * # Behavior
 *
 * ## Example 1
 *
 * If we have mouse movement events W, X, Y, and Z, here is how the rate-limited
 * mouse will handle them:
 *
 * W[         X   ]
 *                 X[   Y        Z  ]
 *                                   Z
 *
 * The rate limited mouse would process them as follows:
 *
 * - W: Fires immediately because no events are queued.
 * - X: Fires after W's timeout window expires.
 * - Y: Gets queued but never fires because Z bumps it.
 * - Z: Replaces Y in the queue and fires at the end of X's timeout window.
 *
 * ## Example 2
 *
 * If we mouse movement events X, Y, and Z, and a mouse click C, here is how the
 * rate-limited mouse will handle them:
 *
 * X[         C  ]
 *            C[     Y      ]
 *                           Y[   Z        ]
 *                                          Z
 *
 * - X: Fires immediately because no events are queued.
 * - C: Fires immediately because clicks are high-priority. It ends the tiemout
 *      and starts a new one.
 * - Y: Fires at the end of C's timeout window.
 * - Z: Fires at the end of Y's timeout window.
 *
 * # Future improvements
 *
 * There is room for improvement if we wanted to further optimize latency or
 * bandwidth. We could potentially queue more elements and use more
 * optimizations to drop unnecessary events:
 *
 * - We can drop some mouse events with a low probability of affecting the
 *     user's experience. For example, if the mouse moves in the following
 *     sequence:
 *
 *       t=0ms (0, 0)
 *       t=1ms (5, 5)
 *       t=2ms (10, 10)
 *
 *     The mouse event at t=1ms is mostly irrelevant because it doesn't matter
 *     to the user whether the mouse stopped at point (5, 5) on the way to
 *     (10, 10).
 * - Some intermediate mouse events do affect user experience. Consider the
 *     following sequence:
 *
 *       t=0ms   (100, 100)
 *       t=20ms  (500, 100)
 *       t=100ms (100, 100)
 *
 *     The mouse ultimately lands in position (100, 100), but dropping the
 *     event at t=20ms might impact user experience if they meant to send a
 *     right-and-left gesture to the target computer.
 * - The more mouse events we queue for transmission after a rate-limit window,
 *     the more latency the user will perceive because we're creating a backlog
 *     of mouse move events for the browser to process.
 */

export class RateLimitedMouse {
  /**
   * @param {number} millisecondsBetweenMouseEvents Number of milliseconds to
   * wait between sending low-priority mouse events to the backend.
   * @param {function(Object)} sendEventFn Function that sends a parsed mouse
   * event to the backend server.
   */
  constructor(millisecondsBetweenMouseEvents, sendEventFn) {
    this._millisecondsBetweenMouseEvents = millisecondsBetweenMouseEvents;
    this._sendEventFn = sendEventFn;
    this._queuedEvent = null;
    this._eventTimer = null;
  }

  onMouseDown(jsMouseEvt) {
    this._processHighPriorityEvent(parseMouseEvent(jsMouseEvt));
  }

  onMouseUp(jsMouseEvt) {
    this._processHighPriorityEvent(parseMouseEvent(jsMouseEvt));
  }

  onMouseMove(jsMouseEvt) {
    this._processLowPriorityEvent(parseMouseEvent(jsMouseEvt));
  }

  onWheel(jsMouseEvt) {
    this._processLowPriorityEvent(parseMouseEvent(jsMouseEvt));
  }

  setTimeoutWindow(millisecondsBetweenMouseEvents) {
    this._millisecondsBetweenMouseEvents = millisecondsBetweenMouseEvents;
  }

  _processHighPriorityEvent(mouseInfo) {
    // Cancel pending event, if one exists.
    this._queuedEvent = null;

    this._emitEvent(mouseInfo);
  }

  _processLowPriorityEvent(mouseInfo) {
    if (this._isInTimeoutWindow()) {
      this._queuedEvent = mouseInfo;
    } else {
      this._emitEvent(mouseInfo);
    }
  }

  /**
   * Emit a mouse event immediately and start a timeout window to gate the next
   * mouse event to send.
   *
   * @param {Object} mouseInfo Mouse information object, parsed from
   * parseMouseEvent.
   */
  _emitEvent(mouseInfo) {
    this._sendEventFn(mouseInfo);
    this._startTimeoutWindow();
  }

  _startTimeoutWindow() {
    // Clear any existing timeout window, if one is set.
    clearTimeout(this._eventTimer); // This is a no-op if _eventTimer is null.
    this._eventTimer = null;

    // Start the timeout window to gate subsequent low-priority events.
    this._eventTimer = setTimeout(() => {
      this._eventTimer = null;
      if (this._queuedEvent) {
        this._emitEvent(this._queuedEvent);
      }
      this._queuedEvent = null;
    }, this._millisecondsBetweenMouseEvents);
  }

  _isInTimeoutWindow() {
    return this._eventTimer !== null;
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
 * Parses a standard JavaScript mouse event into a TinyPilot-specific object
 * containing information about the mouse event.
 *
 * @param {Object} evt A standard JavaScript mouse event, such as mousedown or
 * mousemove.
 * @returns {Object} The mouse event data in TinyPilot-specific format with the
 * following properties:
 * - buttons (number) A bitmask representing which mouse buttons are pressed,
 *   in the same format as the buttons property from the native JavaScript mouse
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
    // TODO(mtlynch): We should move the negation to the server because it's
    // part of converting JS semantics to HID semantics, which is the server's
    // job.
    verticalWheelDelta: normalizeWheelDelta(evt.deltaY) * -1,
    horizontalWheelDelta: normalizeWheelDelta(evt.deltaX),
  };
}
