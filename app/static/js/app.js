"use strict";

const socket = io();
let connected = false;

function onSocketConnect() {
  connected = true;
  document.getElementById('status-connected').style.display = 'inline-block';
  document.getElementById('status-disconnected').style.display = 'none';
  document.getElementById('instructions').style.visibility = 'visible';
  document.getElementById('disconnect-reason').style.visibility = 'hidden';
}

function onSocketDisconnect(reason) {
  connected = false;
  document.getElementById('status-connected').style.display = 'none';
  document.getElementById('status-disconnected').style.display = 'inline-block';
  document.getElementById('disconnect-reason').style.visibility = 'visible';
  document.getElementById('disconnect-reason').innerText = 'Error: ' + reason;
  document.getElementById('instructions').style.visibility = 'hidden';
}

function addKeyCard(key) {
  const card = document.createElement('div');
  card.classList.add('key-card');
  if (key === ' ') {
    card.innerHTML = '&nbsp;';
  } else {
    card.innerText = key;
  }
  const recentKeysDiv = document.getElementById('recent-keys');
  recentKeysDiv.appendChild(card);
  while (recentKeysDiv.childElementCount >= 10) {
    recentKeysDiv.removeChild(recentKeysDiv.firstChild);
  }
}

function onKeyDown(evt) {
  if (!connected) {
    return;
  }
  if (!evt.metaKey) {
    evt.preventDefault();
    addKeyCard(evt.key);
  }
  
  socket.emit('keystroke', {
    altKey: evt.altKey,
    shiftKey: evt.shiftKey,
    ctrlKey: evt.ctrlKey,
    key: evt.key,
    keyCode: evt.keyCode,
  });
}

function onDisplayHistoryChanged(evt) {
  if (evt.target.checked) {
    document.getElementById('recent-keys').style.visibility = 'visible';
  } else {
    document.getElementById('recent-keys').style.visibility = 'hidden';
  }
}

document.querySelector('body').addEventListener("keydown", onKeyDown);
document.getElementById('display-history-checkbox').addEventListener("change", onDisplayHistoryChanged);
socket.on('connect', onSocketConnect);
socket.on('disconnect', onSocketDisconnect);