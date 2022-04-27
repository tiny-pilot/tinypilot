import flask

blueprint = flask.Blueprint('py_license', __name__, url_prefix='/py-license')


@blueprint.route('/tinypilot', methods=['GET'])
def tinypilot_license_get():
    return _make_plaintext_response('LICENSE')


@blueprint.route('/flask', methods=['GET'])
def flask_license_get():
    return 'DUMMY LICENSE'


@blueprint.route('/flask-socketio', methods=['GET'])
def flask_socketio_license_get():
    return _make_plaintext_response(
        'venv/lib/python3.7/site-packages/Flask_SocketIO-5.0.1.dist-info/LICENSE'
    )


def _make_plaintext_response(license_path):
    response = flask.make_response(_read_file(license_path), 200)
    response.mimetype = 'text/plain'
    return response


def _read_file(license_path):
    with open(license_path) as license_file:
        return license_file.read()
