// Suppress ESLint warnings about undefined variables.
// `io` is defined by the Socket.IO library, which is globally available on the
// page.
/* global io */

/**
 * Streams the TinyPilot update logs via a SocketIO connection.
 * @requires socketio
 */
export class UpdateLogsStreamer {
  constructor() {
    // Initilize a Socket on the "/updateLogs" namespace and automatically
    // establish a connection.
    this.socket = io("/updateLogs");
  }

  /**
   * @function handleNewLogs
   * @param {string} logs - The newly received logs.
   *
   * Run a function when new logs are received.
   * @param {handleNewLogs} fn - The function that handles the new logs.
   */
  onNewLogs(fn) {
    // Register the event listener.
    this.socket.on("logs", fn);
  }

  start() {
    this.socket.emit("start");
  }

  stop() {
    this.socket.emit("stop");
  }
}
