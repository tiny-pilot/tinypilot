export class RateLimitedMouse {
  constructor(millisecondsBetweenMouseEvents, sendEventFn) {
    this.millisecondsBetweenMouseEvents = millisecondsBetweenMouseEvents;
    this._sendEventFn = sendEventFn;
    this._eventQueue = [];
    this._eventTimer = null;
  }

  onMouseDown(evt) {
    // Treat mouse down events as high priority. Clear the event queue
    // so that we can process the mouse click immediately. This drops
    // other events, but presumably the mouse click event makes those
    // other events irrelevant, as they hadn't occurred on the target
    // computer at the time the user clicked the mouse.
    this._clearEventQueue();
    this._queueMouseEvent(evt);
  }

  onMouseUp(evt) {
    this._clearEventQueue();
    this._queueMouseEvent(evt);
  }

  onMouseMove(evt) {
    this._queueMouseEvent(evt);
  }

  onWheel(evt) {
    this._queueMouseEvent(evt);
  }

  _queueMouseEvent(evt) {
    const parsedEvent = parseMouseEvent(evt);

    // If there is no timer, send the event immediately but queue any
    // subsequent events that appear within the rate-limit time window.
    if (this._eventTimer === null) {
      this._sendEventFn(parsedEvent);
      this._eventTimer = setTimeout(() => {
        this._dequeueMouseEvent();
      }, this.millisecondsBetweenMouseEvents);
    } else {
      this._eventQueue.push(parsedEvent);
      // Reduce queue to last MAX_MOUSE_EVENT_QUEUE_LENGTH elements.
      this._eventQueue.splice(
        0,
        this._eventQueue.length - MAX_MOUSE_EVENT_QUEUE_LENGTH
      );
    }
  }

  _dequeueMouseEvent() {
    const evt = this._eventQueue.shift();
    if (evt) {
      this._sendEventFn(evt);
    }

    // If we processed the last event in the queue, clear the timer.
    if (this._eventQueue.length === 0) {
      this._eventTimer = null;
    }
    // If there are more events in the queue, process the next event after
    // waiting the rate limit duration.
    else {
      this._eventTimer = setTimeout(() => {
        this._dequeueMouseEvent();
      }, this.millisecondsBetweenMouseEvents);
    }
  }

  _clearEventQueue() {
    clearTimeout(this._eventTimer);
    this._eventTimer = null;
    this._eventQueue.length = 0;
  }
}

// TODO(mtlynch): Figure out ideal queue length.
const MAX_MOUSE_EVENT_QUEUE_LENGTH = 1;

// Different browsers produce wildly different values for wheel scroll
// delta, so just reduce it to -1, 0, or 1.
function normalizeWheelDelta(delta) {
  if (!delta) {
    return 0;
  }
  return Math.sign(delta);
}

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
