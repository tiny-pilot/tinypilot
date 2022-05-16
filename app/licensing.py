import glob

import flask

import json_response

# For code where the source or license is on the local device, prefer linking to
# the locally-available copy instead of the remote URL so that the license ties
# tightly to the version we're using. When that's not possible, look for
# permalink versions of the license that match what we're using.

# pylint: disable=line-too-long
_PROJECTS_METADATA = [
    {
        'name': 'TinyPilot',
        'license_glob_pattern': './LICENSE',
    },
    {
        'name':
            'uStreamer',
        'license_url':
            'https://raw.githubusercontent.com/tiny-pilot/ustreamer/v4.13/LICENSE',
        'homepage_url':
            'https://github.com/pikvm/ustreamer',
    },
    {
        'name': 'Python',
        'homepage_url': 'https://python.org',
        'license_glob_pattern': '/usr/lib/python3.7/LICENSE.txt',
    },
    {
        'name': 'nginx',
        'license_url': 'https://nginx.org/LICENSE',
        'homepage_url': 'https://nginx.org',
    },
    {
        'name':
            'Ansible',
        'homepage_url':
            'https://www.ansible.com',
        'license_url':
            'https://raw.githubusercontent.com/ansible/ansible/v2.9.10/COPYING',
    },
    {
        'name':
            'Janus',
        'homepage_url':
            'https://janus.conf.meetecho.com',
        'license_url':
            'https://raw.githubusercontent.com/tiny-pilot/janus-gateway/v1.0.0/COPYING',
    },

    # JavaScript dependencies.
    {
        'name':
            'webrtc-adapter',
        'homepage_url':
            'https://github.com/webrtcHacks/adapter',
        'license_url':
            'https://github.com/webrtcHacks/adapter/blob/18a8b4127cbc1376320cac5742d817b5b7dd0085/LICENSE.md',
    },
    {
        'name':
            'socket.io',
        'homepage_url':
            'https://socket.io',
        'license_url':
            'https://github.com/socketio/socket.io/blob/3.1.2/LICENSE',
    },

    # Python dependencies, from requirements.txt.
    {
        'name':
            'eventlet',
        'homepage_url':
            'https://eventlet.net',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/eventlet-*.dist-info/LICENSE*',
    },
    {
        'name':
            'Flask',
        'homepage_url':
            'https://flask.palletsprojects.com',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask-*.dist-info/LICENSE*',
    },
    {
        'name':
            'Flask-SocketIO',
        'homepage_url':
            'https://flask-socketio.readthedocs.io',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask_SocketIO-*.dist-info/LICENSE*',
    },
    {
        'name':
            'Flask-WTF',
        'homepage_url':
            'https://flask-wtf.readthedocs.io',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Flask_WTF-*.dist-info/LICENSE*',
    },
    {
        'name':
            'pyyaml',
        'homepage_url':
            'https://pyyaml.org',
        # pyyaml's PyPI package does not include a license, so we have to link
        # to the Github version.
        'license_url':
            'https://raw.githubusercontent.com/yaml/pyyaml/5.4.1/LICENSE',
    },
    {
        'name':
            'bidict',
        'homepage_url':
            'https://bidict.readthedocs.io/en/main',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/bidict-*.dist-info/LICENSE*',
    },
    {
        'name':
            'click',
        'homepage_url':
            'https://palletsprojects.com/p/click',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/click-*.dist-info/LICENSE*',
    },
    {
        'name':
            'dnspython',
        'homepage_url':
            'https://www.dnspython.org',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/dnspython-*.dist-info/LICENSE*',
    },
    {
        'name':
            'greenlet',
        'homepage_url':
            'https://greenlet.readthedocs.io',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/greenlet-*.dist-info/LICENSE*',
    },
    {
        'name':
            'itsdangerous',
        'homepage_url':
            'https://palletsprojects.com/p/itsdangerous/',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/itsdangerous-*.dist-info/LICENSE*',
    },
    {
        'name':
            'Jinja2',
        'homepage_url':
            'https://palletsprojects.com/p/jinja/',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Jinja2-*.dist-info/LICENSE*',
    },
    {
        'name':
            'MarkupSafe',
        'homepage_url':
            'https://palletsprojects.com/p/markupsafe/',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/MarkupSafe-*.dist-info/LICENSE*',
    },
    {
        'name': 'monotonic',
        'homepage_url': 'https://github.com/atdt/monotonic',
        # monotonic's PyPI package does not include a license, so we have to
        # link to the Github version.
        'license_url': 'https://github.com/atdt/monotonic',
    },
    {
        'name':
            'python-engineio',
        'homepage_url':
            'https://github.com/miguelgrinberg/python-engineio',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/python_engineio-*.dist-info/LICENSE*',
    },
    {
        'name':
            'python-socketio',
        'homepage_url':
            'https://github.com/miguelgrinberg/python-socketio',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/python_socketio-*.dist-info/LICENSE*',
    },
    {
        'name':
            'six',
        'homepage_url':
            'https://github.com/benjaminp/six',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/six-*.dist-info/LICENSE*',
    },
    {
        'name':
            'Werkzeug',
        'homepage_url':
            'https://palletsprojects.com/p/werkzeug/',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/Werkzeug-*.dist-info/LICENSE*',
    },
    {
        'name':
            'WTForms',
        'homepage_url':
            'https://wtforms.readthedocs.io',
        'license_glob_pattern':
            './venv/lib/python3.7/site-packages/WTForms-*.dist-info/LICENSE*',
    },

    # Indirect dependencies through Janus.
    {
        'name':
            'libnice',
        'homepage_url':
            'https://gitlab.freedesktop.org/libnice/libnice',
        'license_url':
            'https://gitlab.freedesktop.org/libnice/libnice/-/blob/0.1.18/COPYING',
    },
    {
        'name': 'librtsp',
        'homepage_url': 'https://github.com/cisco/libsrtp',
        'license_url': 'https://github.com/cisco/libsrtp/blob/v2.2.0/LICENSE',
    },
    {
        'name':
            'libwebsockets',
        'homepage_url':
            'https://libwebsockets.org',
        'license_url':
            'https://libwebsockets.org/git/libwebsockets/tree/LICENSE?h=v3.2-stable',
    },

    # Fonts
    {
        'name':
            'Overpass',
        'homepage_url':
            'https://overpassfont.org/',
        'license_glob_pattern':
            './app/static/third-party/fonts/Overpass-License.txt',
    },
]

blueprint = flask.Blueprint('licensing', __name__, url_prefix='/licensing')


@blueprint.route('', methods=['GET'])
def project_metadata_get():
    response = []
    for project in _PROJECTS_METADATA:
        project_name = project['name']
        if project_name == 'TinyPilot':
            continue

        response.append({
            'name': project_name,
            'licenseUrl': '/licensing/%s/license' % project_name,
            'homepageUrl': project['homepage_url'],
        })

    return json_response.success(response)


@blueprint.route('/<project>/license', methods=['GET'])
def project_license_get(project):
    """Retrieves license text for a given project.

    Args:
        project: The name of the project's license to retrieve.

    Returns:
        The contents of the project's license file with text/plain content type.
    """
    project_metadata = _get_project_metadata(project)
    if not project_metadata:
        return flask.make_response('Unknown project', 404)

    if 'license_url' in project_metadata:
        return _make_redirect_response(project_metadata['license_url'])

    license_path = glob.glob(project_metadata['license_glob_pattern'])[0]
    return _make_plaintext_response(license_path)


def _get_project_metadata(project_name):
    for project in _PROJECTS_METADATA:
        if project['name'] == project_name:
            return project
    return None


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
