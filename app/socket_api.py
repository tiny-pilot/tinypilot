import logging

import flask
import flask_socketio

import js_to_hid
import update_logs
from hid import keyboard as fake_keyboard
from hid import mouse as fake_mouse
from hid import write as hid_write
from request_parsers import keystroke as keystroke_request
from request_parsers import mouse_event as mouse_event_request

logger = logging.getLogger(__name__)

socketio = flask_socketio.SocketIO()
socketio.on_namespace(update_logs.Namespace('/updateLogs'))


@socketio.on('keystroke')
def on_keystroke(message):
    logger.debug_sensitive(f'received keystroke message: {message}')
    try:
        keystroke = keystroke_request.parse_keystroke(message)
    except keystroke_request.Error as e:
        logger.error_sensitive(f'Failed to parse keystroke request: {e}')
        return {'success': False}
    hid_keycode = None
    try:
        control_keys, hid_keycode = js_to_hid.convert(keystroke)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning_sensitive(f'Unrecognized key: {keystroke.key} (keycode={keystroke.code})')
        return {'success': False}
    if hid_keycode is None:
        logger.info_sensitive(f'Ignoring {keystroke.key} key (keycode={keystroke.code})')
        return {'success': False}
    keyboard_path = flask.current_app.config.get('KEYBOARD_PATH')
    try:
        fake_keyboard.send_keystroke(keyboard_path, control_keys, hid_keycode)
    except hid_write.WriteError as e:
        logger.error_sensitive(f'Failed to write key: {keystroke.key} (keycode={keystroke.code}). {e}')
        return {'success': False}
    return {'success': True}


@socketio.on('mouse-event')
def on_mouse_event(message):
    try:
        mouse_move_event = mouse_event_request.parse_mouse_event(message)
    except mouse_event_request.Error as e:
        logger.error_sensitive(f'Failed to parse mouse event request: {e}')
        return {'success': False}
    mouse_path = flask.current_app.config.get('MOUSE_PATH')
    try:
        fake_mouse.send_mouse_event(mouse_path, mouse_move_event.buttons,
                                    mouse_move_event.relative_x,
                                    mouse_move_event.relative_y,
                                    mouse_move_event.vertical_wheel_delta,
                                    mouse_move_event.horizontal_wheel_delta)
    except hid_write.WriteError as e:
        logger.error_sensitive(f'Failed to forward mouse event: {e}')
        return {'success': False}
    return {'success': True}


@socketio.on('keyRelease')
def on_key_release():
    keyboard_path = flask.current_app.config.get('KEYBOARD_PATH')
    try:
        fake_keyboard.release_keys(keyboard_path)
    except hid_write.WriteError as e:
        logger.error_sensitive(f'Failed to release keys: {e}')


@socketio.on('connect')
def on_connect():
    logger.info('Client %s connected', flask.request.sid)


@socketio.on('disconnect')
def on_disconnect():
    logger.info('Client %s disconnected', flask.request.sid)
