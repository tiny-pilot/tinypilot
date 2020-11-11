"use strict";

// Send a keystroke message to the backend.
export function sendKeystroke(socket, keystroke) {
  return new Promise((resolve, reject) => {
    socket.emit("keystroke", keystroke, (result) => {
      if (result.success) {
        resolve({});
      } else {
        reject(new Error("Failed to forward keystroke"));
      }
    });
  });
}
