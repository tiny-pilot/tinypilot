/**
 * A mechanism to rate-limit the keystrokes messages sent to backend so that
 * they don't flood the SocketIO server's message queue and starve the server of
 * PING/PONG messages, needed to keep the client-server connection alive.
 *
 * The current rate-limiting implementation maintains an array of anonymous
 * functions that get executed in a first in, first out (FIFO) ordering at a
 * fixed rate of 20 functions per second (i.e., a function gets executed once
 * every 50ms). Once a function has been executed, it is removed from the array.
 * Each enqueue function is responsible for it's own success/error handling.
 */
export class RateLimitedKeystrokes {
  /**
   * @param {Socket} socket - https://socket.io/docs/v4/client-api/#socket
   */
  constructor(socket) {
    this._socket = socket;
    this._eventQueue = [];
    setInterval(this._runEvent.bind(this), 50 /* 20 events per second */);
  }

  _runEvent() {
    const eventFunc = this._eventQueue.shift();
    if (eventFunc === undefined) {
      return;
    }
    eventFunc();
  }

  _queueEvent(eventFunc) {
    this._eventQueue.push(eventFunc);
  }

  _handleKeystroke(keystroke, resolve, reject) {
    this._socket.emit("keystroke", keystroke, (result) => {
      if ("success" in result && result.success) {
        resolve({});
      } else {
        reject(new Error("Failed to forward keystroke"));
      }
    });
  }

  /**
   * Enqueue a keystroke message to be sent to the backend.
   * @param {Object} keystroke - An object as returned by `processKeystroke`
   * @returns {Promise<Object>}
   *     Success case:  the Promise resolves with an empty object.
   *     Error case:    the Promise rejects with an `Error`.
   */
  sendKeystroke(keystroke) {
    return new Promise((resolve, reject) => {
      this._queueEvent(() => this._handleKeystroke(keystroke, resolve, reject));
    });
  }

  /**
   * Enqueue a keyRelease message to be sent to the backend.
   */
  sendKeyRelease() {
    this._queueEvent(() => this._socket.emit("keyRelease"));
  }
}
