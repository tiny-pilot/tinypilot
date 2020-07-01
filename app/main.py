#!/usr/bin/env python

import logging
import os

import flask
import flask_socketio
import flask_wtf

import hid
import js_to_hid
import local_system

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
root_logger.setLevel(logging.INFO)

app = flask.Flask(__name__, static_url_path='')
socketio = flask_socketio.SocketIO(app)

# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)
app.config['SECRET_KEY'] = os.urandom(32)

logger = logging.getLogger(__name__)
logger.info('Starting app')

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 8000))
debug = 'DEBUG' in os.environ
# Location of HID file handle in which to write keyboard HID input.
hid_path = os.environ.get('HID_PATH', '/dev/hidg0')


def _parse_key_event(payload):
    return js_to_hid.JavaScriptKeyEvent(meta_modifier=payload['metaKey'],
                                        alt_modifier=payload['altKey'],
                                        shift_modifier=payload['shiftKey'],
                                        ctrl_modifier=payload['ctrlKey'],
                                        key=payload['key'],
                                        key_code=payload['keyCode'])


@socketio.on('keystroke')
def socket_keystroke(message):
    key_event = _parse_key_event(message)
    hid_keycode = None
    try:
        control_keys, hid_keycode = js_to_hid.convert(key_event)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning('Unrecognized key: %s (keycode=%d)', key_event.key,
                       key_event.key_code)
        socketio.emit('keystroke-received', {'success': False})
        return
    if hid_keycode is None:
        logger.info('Ignoring %s key (keycode=%d)', key_event.key,
                    key_event.key_code)
        socketio.emit('keystroke-received', {'success': False})
        return
    try:
        hid.send(hid_path, control_keys, hid_keycode)
    except hid.WriteError as e:
        logger.error('Failed to write key: %s (keycode=%d). %s', key_event.key,
                     key_event, e)
        socketio.emit('keystroke-received', {'success': False})
        return
    socketio.emit('keystroke-received', {'success': True})


@socketio.on('connect')
def test_connect():
    logger.info('Client connected')


@socketio.on('disconnect')
def test_disconnect():
    logger.info('Client disconnected')


@app.route('/', methods=['GET'])
def index_get():
    return flask.render_template('index.html')


@app.route('/shutdown', methods=['POST'])
def shutdown_post():
    try:
        local_system.shutdown()
        return flask.jsonify({
            'success': True,
            'error': None,
        })
    except local_system.Error as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500


@app.errorhandler(flask_wtf.csrf.CSRFError)
def handle_csrf_error(e):
    return flask.jsonify({
        'success': False,
        'error': e.description,
    }), 400


if __name__ == '__main__':
    socketio.run(app,
                 host=host,
                 port=port,
                 debug=debug,
                 use_reloader=True,
                 extra_files=[
                     './app/templates/index.html', './app/static/js/app.js',
                     './app/static/css/style.css'
                 ])
