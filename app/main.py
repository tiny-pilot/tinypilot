#!/usr/bin/env python

import logging
import os

import flask
import flask_socketio
import flask_wtf

import js_to_hid
import local_system
from find_files import find as find_files
from hid import keyboard as fake_keyboard
from hid import mouse as fake_mouse
from hid import write as hid_write
from request_parsers import keystroke as keystroke_request
from request_parsers import mouse_event as mouse_event_request
from flask import request

host = os.environ.get('HOST', '0.0.0.0')
port = int(os.environ.get('PORT', 8000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '1') == '1'
# Location of file path at which to write keyboard HID input.
keyboard_path = os.environ.get('KEYBOARD_PATH', '/dev/hidg0')
# Location of file path at which to write mouse HID input.
mouse_path = os.environ.get('MOUSE_PATH', '/dev/hidg1')
# Keyboard layout on target computer.
keyboard_layout = os.environ.get('KEYBOARD_LAYOUT', 'QWERTY')

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    # Socket.io logs are too chatty at INFO level.
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.info('Starting app')

app = flask.Flask(__name__, static_url_path='')
app.config['TEMPLATES_AUTO_RELOAD'] = True
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
                                    mouse_move_event.relative_y)
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


@app.route('/', methods=['GET'])
def index_get():
    return flask.render_template(
        'index.html', custom_elements_files=find_files.custom_elements_files())


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

@app.route("/mountRemoteFs", methods=['POST'])
def mountRemoteFs():
    try:
        shareType = request.form.get("shareType")
        sharePath = request.form.get("sharePath")
        userName = request.form.get("shareUser")
        password = request.form.get("sharePassword")
        cmd = "sudo /opt/tinypilot/scripts/mountShare " + str(shareType) + " \"" +str(sharePath) + "\""
        if userName != "":
            cmd = cmd + " " + str(userName) + " \"" + str(password) + "\""
        exitCode = os.system(cmd)
        retValue = True
        if exitCode != 0:
            retValue = False  
        return flask.jsonify({
            'success': retValue,
            'error': None,
            'command': cmd,
        })
    except Exception as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500

@app.route("/getRemoteFsContent", methods=['GET'])
def getRemoteFsContent():
    try:
        retValue = os.system("mount | grep /tmp/remoteFs")
        if retValue != 0:
            return flask.jsonify({
                'success': False,
                'error': "File not mounted",
            }), 500
        f = []
        d = []
        path = "/tmp/remoteFs/"
        subDir = request.args.get("subPath")
        if subDir is None:
            pass
        else:
            if subDir.find("../") != -1 or subDir.endswith(".."):
                return flask.jsonify({
                'success': False,
                'error': ".. not allowed",
                'path': None,
                'data': None 
            })
            path = path + subDir
            
        for (dirpath, dirnames, filenames) in os.walk(path):
            return flask.jsonify({
                'success': True,
                'error': None,
                'path': path,
                'data': [dirnames, filenames] 
            })
        return flask.jsonify({
                'success': True,
                'error': None,
                'data': {},
                'path': path 
            })
    except Exception as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500

@app.route('/MountImage')
def MountImage():
    try:
        imageFile = request.args.get("Path")
        if imageFile.find("../") != -1 or imageFile.endswith(".."):
                return flask.jsonify({
                'success': False,
                'error': ".. not allowed",
            })
        msdType = request.args.get("type")

        cmd = "sudo /opt/tinypilot/scripts/mountImage " + msdType + " \"" + imageFile + "\""
        os.system(cmd)
        return flask.jsonify({
            'success': True,
            'cmd': cmd,
            'error': None,
        })
        pass
    except Exception as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500

@app.route("/ClearImage")
def ClearImage():
    try:
        cmd = "/opt/tinypilot/scripts/clearImage"
        os.system(cmd)
        return flask.jsonify({
            'success': True,
            'cmd': cmd,
            'error': None,
        })
        pass
    except Exception as e:
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
                 extra_files=find_files.all_frontend_files())


if __name__ == '__main__':
    main()
