/**
 * Streams the TinyPilot update logs via a SocketIO connection.
 * @requires socketio
 */
class UpdateLogsStreamer {
  constructor() {
    // Initilize a Socket on the "/updateLogs" namespace and automatically
    // establish a connection.
    this.socket = io("/updateLogs");
  }

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
