import datetime
import functools
import logging

import flask
import flask_socketio

import auth
import env
import js_to_hid
import session
import update_logs
import utc
from hid import keyboard as fake_keyboard
from hid import mouse as fake_mouse
from hid import write as hid_write
from request_parsers import keystroke as keystroke_request
from request_parsers import mouse_event as mouse_event_request

logger = logging.getLogger(__name__)

socketio = flask_socketio.SocketIO()
socketio.on_namespace(update_logs.Namespace('/updateLogs'))

# A mapping from socket id to timestamps, which is used by
# `@monitor_auth`. The timestamp is when the next authentication check is due
# for the respective socket connection.
_auth_expiry_timestamps = {}


def monitor_auth(handler):
    """Decorator that monitors the session’s auth state of the socket.

    When socket events come in, it checks whether the session still satisfies
    the auth requirement by making calls to `session.is_auth_valid()`. If the
    session’s auth state has become invalid, it disconnects the client.

    It doesn’t carry out the check for every incoming socket event, but it
    caches the result for a short amount of time, before triggering a fresh
    check. The reason is that a call to `session.is_auth_valid()` might take
    several milliseconds, and we don’t want to add that latency on every single
    incoming socket event. So the periodic caching behaviour is a tradeoff
    between security and performance.

    Example of usage:
        @monitor_auth
        def on_socket_event():
            ...
    """
    cache_ttl_seconds = 10

    @functools.wraps(handler)
    def handler_with_auth_check(*args, **kwargs):
        next_check_due = _auth_expiry_timestamps.get(flask.request.sid, None)

        if (not next_check_due) or (utc.now() > next_check_due):
            if not session.is_auth_valid(satisfies_role=auth.Role.OPERATOR):
                flask_socketio.disconnect()
                return None

            _auth_expiry_timestamps[flask.request.sid] = utc.now(
            ) + datetime.timedelta(seconds=cache_ttl_seconds)

        return handler(*args, **kwargs)

    return handler_with_auth_check


@socketio.on('keystroke')
@monitor_auth
def on_keystroke(message):
    logger.debug_sensitive('received keystroke message: %s', message)
    try:
        keystroke = keystroke_request.parse_keystroke(message)
    except keystroke_request.Error as e:
        logger.error_sensitive('Failed to parse keystroke request: %s', e)
        return {'success': False}
    try:
        hid_keystroke = js_to_hid.convert(keystroke)
    except js_to_hid.UnrecognizedKeyCodeError:
        logger.warning_sensitive('Unrecognized key: %s (keycode=%s)',
                                 keystroke.key, keystroke.code)
        return {'success': False}
    keyboard_path = env.KEYBOARD_PATH
    try:
        fake_keyboard.send_keystroke(keyboard_path, hid_keystroke)
    except hid_write.WriteError as e:
        logger.error_sensitive('Failed to write key: %s (keycode=%s). %s',
                               keystroke.key, keystroke.code, e)
        return {'success': False}
    return {'success': True}


@socketio.on('mouse-event')
@monitor_auth
def on_mouse_event(message):
    try:
        mouse_move_event = mouse_event_request.parse_mouse_event(message)
    except mouse_event_request.Error as e:
        logger.error_sensitive('Failed to parse mouse event request: %s', e)
        return {'success': False}
    mouse_path = env.MOUSE_PATH
    try:
        fake_mouse.send_mouse_event(mouse_path, mouse_move_event.buttons,
                                    mouse_move_event.relative_x,
                                    mouse_move_event.relative_y,
                                    mouse_move_event.vertical_wheel_delta,
                                    mouse_move_event.horizontal_wheel_delta)
    except hid_write.WriteError as e:
        logger.error_sensitive('Failed to forward mouse event: %s', e)
        return {'success': False}
    return {'success': True}


@socketio.on('keyRelease')
@monitor_auth
def on_key_release():
    keyboard_path = env.KEYBOARD_PATH
    try:
        fake_keyboard.release_keys(keyboard_path)
    except hid_write.WriteError as e:
        logger.error_sensitive('Failed to release keys: %s', e)


@socketio.on('connect')
def on_connect():
    if not session.is_auth_valid(satisfies_role=auth.Role.OPERATOR):
        return False
    logger.info('Client %s connected', flask.request.sid)
    return True


@socketio.on('disconnect')
def on_disconnect():
    if flask.request.sid in _auth_expiry_timestamps:
        del _auth_expiry_timestamps[flask.request.sid]
    logger.info('Client %s disconnected', flask.request.sid)
