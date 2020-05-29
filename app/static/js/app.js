"use strict";

const socket = io.connect('http://' + document.domain + ':' + location.port + '/test');

function onKeyDown(evt) {
  evt.preventDefault();
  
  socket.emit('keystroke', {
    altKey: evt.altKey,
    shiftKey: evt.shiftKey,
    ctrlKey: evt.ctrlKey,
    key: evt.key,
    keyCode: evt.keyCode,
  });
}

document.getElementById("virtual-console").addEventListener("keydown", onKeyDown);
