import logging

import flask

import hid
import js_to_hid

root_logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-15s %(levelname)-4s %(message)s', '%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
root_logger.addHandler(flask.logging.default_handler)
root_logger.setLevel(logging.INFO)

app = flask.Flask(__name__)

logger = logging.getLogger(__name__)
logger.info('Starting app')


@app.route('/virtual-keyboard', methods=['POST'])
def virtual_keyboard_post():
    payload = flask.request.json
    hid_keycode = js_to_hid.convert(payload.keyCode)
    hid.send(hid_keycode)
    response = flask.jsonify(payload)
    return response