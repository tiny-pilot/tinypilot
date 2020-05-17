import logging

import flask

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


# TODO: Make CORS based on command-line

@app.route('/virtual-keyboard', methods=['OPTIONS'])
def virtual_keyboard_options():
    response = flask.jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Accept')
    return response

@app.route('/virtual-keyboard', methods=['POST'])
def virtual_keyboard_post():
    payload = flask.request.json
    response = flask.jsonify(payload)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response