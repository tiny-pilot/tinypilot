#!/usr/bin/env python

import logging
import os

import flask
import flask_socketio
import flask_wtf

import js_to_hid
import local_system
from hid import keyboard as fake_keyboard
from hid import mouse as fake_mouse
from hid import write as hid_write

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.info('Starting app')

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 8000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '1') == '1'
# Location of file path at which to write keyboard HID input.
keyboard_path = os.environ.get('KEYBOARD_PATH', '/dev/hidg0')
# Location of file path at which to write mouse HID input.
mouse_path = os.environ.get('MOUSE_PATH', '/dev/hidg1')

# Socket.io logs are too chatty at INFO level.
if not debug:
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

app = flask.Flask(__name__, static_url_path='')
# TODO(mtlynch): Ideally, we wouldn't accept requests from any origin, but the
# risk of a CSRF attack for this app is very low. Additionally, CORS doesn't
# protect us from the dangerous part of a CSRF attack. Even without same-origin
# enforcement, third-party pages can still *send* requests (i.e. inject
# keystrokes into the target machine) - it doesn't matter much if they can't
# read responses.
socketio = flask_socketio.SocketIO(app, cors_allowed_origins='*')

# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)
app.config['SECRET_KEY'] = os.urandom(32)


def _parse_key_event(payload):
    return js_to_hid.JavaScriptKeyEvent(meta_modifier=payload['metaKey'],
                                        alt_modifier=payload['altKey'],
                                        shift_modifier=payload['shiftKey'],
                                        ctrl_modifier=payload['ctrlKey'],
                                        key=payload['key'],
                                        key_code=payload['keyCode'],
                                        keystroke_id=payload['keystrokeId'])


def _parse_mouse_move_event(payload):
    return js_to_hid.JavaScriptMouseMoveEvent(x=max(0, payload['x']),
                                              y=max(0, payload['y']),
                                              mouse_down=payload['mouseDown'],
                                              mouse_button=payload['mouseButton'])


@socketio.on('keystroke')
def socket_keystroke(message):
    key_event = _parse_key_event(message)
    hid_keycode = None
    processing_result = {
        'keystrokeId': key_event.keystroke_id,
        'success': False
    }
    try:
        control_keys, hid_keycode = js_to_hid.convert(key_event)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning('Unrecognized key: %s (keycode=%d)', key_event.key,
                       key_event.key_code)
        socketio.emit('keystroke-received', processing_result)
        return
    if hid_keycode is None:
        logger.info('Ignoring %s key (keycode=%d)', key_event.key,
                    key_event.key_code)
        socketio.emit('keystroke-received', processing_result)
        return
    try:
        fake_keyboard.send_keystroke(keyboard_path, control_keys, hid_keycode)
    except hid_write.WriteError as e:
        logger.error('Failed to write key: %s (keycode=%d). %s', key_event.key,
                     key_event.key_code, e)
        socketio.emit('keystroke-received', processing_result)
        return
    processing_result['success'] = True
    socketio.emit('keystroke-received', processing_result)


@socketio.on('mouseMovement')
def socket_mouse_movement(message):
    mouse_move_event = _parse_mouse_move_event(message)
    try:
        fake_mouse.send_mouse_position(mouse_path, mouse_move_event.x,
                                       mouse_move_event.y,
                                       mouse_move_event.mouse_down,
                                       mouse_move_event.mouse_button)
    except hid_write.WriteError as e:
        logger.error('Failed to forward mouse movement: %s', e)
    socketio.emit('mouse-movement-received', {'success': True})


@socketio.on('keyRelease')
def socket_key_release():
    try:
        fake_keyboard.release_keys(keyboard_path)
    except hid_write.WriteError as e:
        logger.error('Failed to release keys: %s', e)


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


@app.route('/restart', methods=['POST'])
def restart_post():
    try:
        local_system.restart()
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


def main():
    socketio.run(app,
                 host=host,
                 port=port,
                 debug=debug,
                 use_reloader=use_reloader,
                 extra_files=[
                     './app/templates/index.html', './app/static/js/app.js',
                     './app/static/css/style.css'
                 ])


if __name__ == '__main__':
    main()
