import glob

import flask

_LICENSE_PATTERNS = {
    'tinypilot':
        'LICENSE',
    'python':
        '/usr/lib/python3.7/LICENSE.txt',
    'eventlet':
        'venv/lib/python3.7/site-packages/eventlet-*.dist-info/LICENSE*',
    'Flask':
        'venv/lib/python3.7/site-packages/Flask-*.dist-info/LICENSE*',
    'Flask-SocketIO':
        'venv/lib/python3.7/site-packages/Flask_SocketIO-*.dist-info/LICENSE*',
    'Flask-WTF':
        'venv/lib/python3.7/site-packages/Flask_WTF-*.dist-info/LICENSE*',
    # pyyaml's PyPI package does not include a license, so we skip pyyaml.
    'bidict':
        'venv/lib/python3.7/site-packages/bidict-*.dist-info/LICENSE*',
    'click':
        'venv/lib/python3.7/site-packages/click-*.dist-info/LICENSE*',
    'dnspython':
        'venv/lib/python3.7/site-packages/dnspython-*.dist-info/LICENSE*',
    'greenlet':
        'venv/lib/python3.7/site-packages/greenlet-*.dist-info/LICENSE*',
    'itsdangerous':
        'venv/lib/python3.7/site-packages/itsdangerous-*.dist-info/LICENSE*',
    'Jinja2':
        'venv/lib/python3.7/site-packages/Jinja2-*.dist-info/LICENSE*',
    'MarkupSafe':
        'venv/lib/python3.7/site-packages/MarkupSafe-*.dist-info/LICENSE*',
    # monotonic's PyPI package does not include a license, so we skip monotonic.
    'python-engineio':
        'venv/lib/python3.7/site-packages/python_engineio-*.dist-info/LICENSE*',
    'python-socketio':
        'venv/lib/python3.7/site-packages/python_socketio-*.dist-info/LICENSE*',
    'six':
        'venv/lib/python3.7/site-packages/six-*.dist-info/LICENSE*',
    'Werkzeug':
        'venv/lib/python3.7/site-packages/Werkzeug-*.dist-info/LICENSE*',
    'WTForms':
        'venv/lib/python3.7/site-packages/WTForms-*.dist-info/LICENSE*',
}

blueprint = flask.Blueprint('py_license', __name__, url_prefix='/py-license')


@blueprint.route('/<project>', methods=['GET'])
def python_project_license_get(project):
    try:
        return _make_plaintext_response(_get_license_path(project))
    except KeyError:
        return flask.make_response('Unknown project', 404)


def _get_license_path(project):
    return glob.glob(_LICENSE_PATTERNS[project])[0]


def _make_plaintext_response(license_path):
    response = flask.make_response(_read_file(license_path), 200)
    response.mimetype = 'text/plain'
    return response


def _read_file(license_path):
    with open(license_path) as license_file:
        return license_file.read()
