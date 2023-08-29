export class RateLimitedKeyboard {
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

  _handleKeystroke(keystroke, resolve, reject) {
    this._socket.emit("keystroke", keystroke, (result) => {
      if ("success" in result && result.success) {
        resolve({});
      } else {
        reject(new Error("Failed to forward keystroke"));
      }
    });
  }

  // Enqueue a keystroke message to be sent to the backend.
  sendKeystroke(keystroke) {
    return new Promise((resolve, reject) => {
      this._eventQueue.push(() =>
        this._handleKeystroke(keystroke, resolve, reject)
      );
    });
  }
}
