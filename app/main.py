#!/usr/bin/env python

import logging

import flask
import flask_socketio

import hid
import js_to_hid

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
root_logger.setLevel(logging.INFO)

app = flask.Flask(__name__, static_url_path='')
socketio = flask_socketio.SocketIO(app)

logger = logging.getLogger(__name__)
logger.info('Starting app')


def _parse_key_event(payload):
    return js_to_hid.JavaScriptKeyEvent(alt_key=payload['altKey'],
                                        shift_key=payload['shiftKey'],
                                        ctrl_key=payload['ctrlKey'],
                                        key=payload['key'],
                                        key_code=payload['keyCode'])


@socketio.on('keystroke')
def socket_keystroke(message):
    key_event = _parse_key_event(message)
    try:
        control_keys, hid_keycode = js_to_hid.convert(key_event)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning('Unrecognized key: %s (keycode=%d)', key_event.key,
                       key_event.key_code)
        return
    if hid_keycode is None:
        logger.info('Ignoring %s key (keycode=%d)', key_event.key,
                    key_event.key_code)
    else:
        # TODO: Re-enable
        #hid.send(control_keys, hid_keycode)
        pass


@socketio.on('connect')
def test_connect():
    logger.info('Client connected')


@socketio.on('disconnect')
def test_disconnect():
    logger.info('Client disconnected')


@app.route('/', methods=['GET'])
def index_get():
    return flask.render_template('index.html')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8001)
