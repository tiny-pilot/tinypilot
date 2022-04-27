import flask

# TODO: Replace the version numbers with globs.
_LICENSE_PATHS = {
    'flask-socketio':
        'venv/lib/python3.7/site-packages/Flask_SocketIO-5.0.1.dist-info/LICENSE',
    'Flask-WTF':
        'venv/lib/python3.7/site-packages/Flask_WTF-0.14.3.dist-info/LICENSE',
    'python':
        '/usr/lib/python3.7/LICENSE.txt',
    'tinypilot':
        'LICENSE',
}

blueprint = flask.Blueprint('py_license', __name__, url_prefix='/py-license')


@blueprint.route('/<project>', methods=['GET'])
def python_project_license_get(project):
    try:
        return _make_plaintext_response(_LICENSE_PATHS[project])
    except KeyError:
        return flask.make_response('Unknown project', 404)


def _make_plaintext_response(license_path):
    response = flask.make_response(_read_file(license_path), 200)
    response.mimetype = 'text/plain'
    return response


def _read_file(license_path):
    with open(license_path) as license_file:
        return license_file.read()
