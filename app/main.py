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


def _parse_key_event(payload):
    return js_to_hid.JavaScriptKeyEvent(alt_key=payload['altKey'],
                                        shift_key=payload['shiftKey'],
                                        ctrl_key=payload['ctrlKey'],
                                        key=payload['key'],
                                        key_code=payload['keyCode'])


@app.route('/virtual-keyboard', methods=['POST'])
def virtual_keyboard_post():
    key_event = _parse_key_event(flask.request.json['keyEvent'])
    sequence_number = int(flask.request.json['sequenceNumber'])
    try:
        control_keys, hid_keycode = js_to_hid.convert(key_event)
    except UnrecognizedKeyCodeError:
        logger.warning('Unrecognized key: %s (keycode=%d)', key_event.key,
                       key_event.key_code)
        return flask.jsonify({
            'processed': True,
            'queued': False,
            'ignored': True,
            'lastSequenceNumberProcessed': sequence_number
        })
    ignored = False
    if hid_keycode is None:
        logger.info('Ignoring %s key (keycode=%d)', key_event.key,
                    key_event.key_code)
        ignored = True
    else:
        hid.send(control_keys, hid_keycode)

    return flask.jsonify({
        'processed': True,
        'queued': False,
        'ignored': ignored,
        'lastSequenceNumberProcessed': sequence_number
    })
