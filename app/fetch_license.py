import flask

blueprint = flask.Blueprint('py_license', __name__, url_prefix='/py-license')


@blueprint.route('/tinypilot', methods=['GET'])
def tinypilot_license_get():
    response = flask.make_response(_read_file('LICENSE'), 200)
    response.mimetype = 'text/plain'
    return response


@blueprint.route('/flask', methods=['GET'])
def flask_license_get():
    return 'DUMMY LICENSE'


def _read_file(license_path):
    with open(license_path) as license_file:
        return license_file.read()
