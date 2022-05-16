import glob

import flask

# pylint: disable=line-too-long
_PROJECTS_METADATA = {
    'TinyPilot': {
        'license_glob_pattern': './LICENSE',
    },
    'Python': {
        'license_glob_pattern': '/usr/lib/python3.7/LICENSE.txt',
    },
    'uStreamer': {
        'license_url':
            'https://raw.githubusercontent.com/tiny-pilot/ustreamer/v4.13/LICENSE',
    },
    'nginx': {
        'license_url': 'https://nginx.org/LICENSE',
    },
    'Ansible': {
        'license_url':
            'https://raw.githubusercontent.com/ansible/ansible/v2.9.10/COPYING',
    },
    'Janus': {
        'license_url':
            'https://raw.githubusercontent.com/tiny-pilot/janus-gateway/v1.0.0/COPYING',
    },

    # JavaScript dependencies.
    'webrtc-adapter': {
        'license_url':
            'https://github.com/webrtcHacks/adapter/blob/18a8b4127cbc1376320cac5742d817b5b7dd0085/LICENSE.md',
    },
    'socket.io': {
        'license_url':
            'https://github.com/socketio/socket.io/blob/3.1.2/LICENSE',
    },

    # From requirements.txt
    'eventlet': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/eventlet-*.dist-info/LICENSE*',
    },
    'Flask': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask-*.dist-info/LICENSE*',
    },
    'Flask-SocketIO': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask_SocketIO-*.dist-info/LICENSE*',
    },
    'Flask-WTF': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask_WTF-*.dist-info/LICENSE*',
    },
    # pyyaml's PyPI package does not include a license, so we have to link to
    # the Github version.
    'pyyaml': {
        'license_url':
            'https://raw.githubusercontent.com/yaml/pyyaml/5.4.1/LICENSE',
    },
    'bidict': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/bidict-*.dist-info/LICENSE*',
    },
    'click': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/click-*.dist-info/LICENSE*',
    },
    'dnspython': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/dnspython-*.dist-info/LICENSE*',
    },
    'greenlet': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/greenlet-*.dist-info/LICENSE*',
    },
    'itsdangerous': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/itsdangerous-*.dist-info/LICENSE*',
    },
    'Jinja2': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Jinja2-*.dist-info/LICENSE*',
    },
    'MarkupSafe': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/MarkupSafe-*.dist-info/LICENSE*',
    },
    # monotonic's PyPI package does not include a license, so we have to link to
    # the Github version.
    'monotonic': {
        'license_url': 'https://github.com/atdt/monotonic',
    },
    'python-engineio': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/python_engineio-*.dist-info/LICENSE*',
    },
    'python-socketio': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/python_socketio-*.dist-info/LICENSE*',
    },
    'six': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/six-*.dist-info/LICENSE*',
    },
    'Werkzeug': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Werkzeug-*.dist-info/LICENSE*',
    },
    'WTForms': {
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/WTForms-*.dist-info/LICENSE*',
    },

    # Indirect dependencies through Janus.
    'libnice': {
        'license_url':
            'https://gitlab.freedesktop.org/libnice/libnice/-/blob/0.1.18/COPYING',
    },
    'librtsp': {
        'license_url':
            'https://libwebsockets.org/git/libwebsockets/tree/LICENSE?h=v3.2-stable',
    },
}

blueprint = flask.Blueprint('py_license', __name__, url_prefix='/license')


@blueprint.route('/<project>', methods=['GET'])
def python_project_license_get(project):
    """Retrieves license text for a given Python project.

    Args:
        project: The name of the Python project's license to retrieve.

    Returns:
        The contents of the project's license file with text/plain content type.
    """

    try:
        project_metadata = _get_project_metadata(project)
    except KeyError:
        return flask.make_response('Unknown project', 404)

    if 'license_url' in project_metadata:
        return _make_redirect_response(project_metadata['license_url'])

    license_path = glob.glob(project_metadata['license_glob_pattern'])[0]
    return _make_plaintext_response(license_path)


def _get_project_metadata(project):
    return _PROJECTS_METADATA[project]


def _make_plaintext_response(license_pattern):
    license_path = glob.glob(license_pattern)[0]
    response = flask.make_response(_read_file(license_path), 200)
    response.mimetype = 'text/plain'
    return response


def _read_file(license_path):
    with open(license_path) as license_file:
        return license_file.read()


def _make_redirect_response(license_url):
    return flask.redirect(license_url, code=302)
