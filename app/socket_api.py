import logging
import os

import flask_socketio

import js_to_hid
from hid import keyboard as fake_keyboard
from hid import mouse as fake_mouse
from hid import write as hid_write
from request_parsers import keystroke as keystroke_request
from request_parsers import mouse_event as mouse_event_request

logger = logging.getLogger(__name__)

# TODO(mtlynch): Move these environment variables to a config file.

# Location of file path at which to write keyboard HID input.
keyboard_path = os.environ.get('KEYBOARD_PATH', '/dev/hidg0')
# Location of file path at which to write mouse HID input.
mouse_path = os.environ.get('MOUSE_PATH', '/dev/hidg1')
# Keyboard layout on target computer.
keyboard_layout = os.environ.get('KEYBOARD_LAYOUT', 'QWERTY')

# TODO(mtlynch): Ideally, we wouldn't accept requests from any origin, but the
# risk of a CSRF attack for this app is very low. Additionally, CORS doesn't
# protect us from the dangerous part of a CSRF attack. Even without same-origin
# enforcement, third-party pages can still *send* requests (i.e. inject
# keystrokes into the target machine) - it doesn't matter much if they can't
# read responses.
socketio = flask_socketio.SocketIO(cors_allowed_origins='*')


@socketio.on('keystroke')
def socket_keystroke(message):
    try:
        keystroke = keystroke_request.parse_keystroke(message)
    except keystroke_request.Error as e:
        logger.error('Failed to parse keystroke request: %s', e)
        return
    hid_keycode = None
    try:
        control_keys, hid_keycode = js_to_hid.convert(keystroke,
                                                      keyboard_layout)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning('Unrecognized key: %s (keycode=%d)', keystroke.key,
                       keystroke.key_code)
        return {'success': False}
    if hid_keycode is None:
        logger.info('Ignoring %s key (keycode=%d)', keystroke.key,
                    keystroke.key_code)
        return {'success': False}
    try:
        fake_keyboard.send_keystroke(keyboard_path, control_keys, hid_keycode)
    except hid_write.WriteError as e:
        logger.error('Failed to write key: %s (keycode=%d). %s', keystroke.key,
                     keystroke.key_code, e)
        return {'success': False}
    return {'success': True}


@socketio.on('mouse-event')
def socket_mouse_event(message):
    try:
        mouse_move_event = mouse_event_request.parse_mouse_event(message)
    except mouse_event_request.Error as e:
        logger.error('Failed to parse mouse event request: %s', e)
        return {'success': False}
    try:
        fake_mouse.send_mouse_event(mouse_path, mouse_move_event.buttons,
                                    mouse_move_event.relative_x,
                                    mouse_move_event.relative_y,
                                    mouse_move_event.vertical_wheel_delta,
                                    mouse_move_event.horizontal_wheel_delta)
    except hid_write.WriteError as e:
        logger.error('Failed to forward mouse event: %s', e)
        return {'success': False}
    return {'success': True}


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
