import dataclasses
import glob

import flask

import json_response


@dataclasses.dataclass
class LicenseMetadata:
    name: str
    homepage_url: str
    # The license_glob_pattern and license_url properties are mutually
    # exclusive.
    # Glob pattern that points to the license file on the local system.
    license_glob_pattern: str = ''
    # URL of license file if it's not available on the local system.
    license_url: str = ''


# For code where the source or license is on the local device, prefer linking to
# the locally-available copy instead of the remote URL so that the license ties
# tightly to the version we're using. When that's not possible, look for
# permalink versions of the license that match the version of the software we're
# using.

# pylint: disable=line-too-long
_LICENSE_METADATA = [
    LicenseMetadata(name='TinyPilot',
                    license_glob_pattern='./LICENSE',
                    homepage_url='https://tinypilotkvm.com'),
    LicenseMetadata(
        name='uStreamer',
        license_url=
        'https://raw.githubusercontent.com/tiny-pilot/ustreamer/v4.13/LICENSE',
        homepage_url='https://github.com/pikvm/ustreamer'),
    LicenseMetadata(name='Python',
                    homepage_url='https://python.org',
                    license_glob_pattern='/usr/lib/python3.7/LICENSE.txt'),
    LicenseMetadata(name='nginx',
                    license_url='https://nginx.org/LICENSE',
                    homepage_url='https://nginx.org'),
    LicenseMetadata(
        name='Janus',
        homepage_url='https://janus.conf.meetecho.com',
        license_url=
        'https://raw.githubusercontent.com/tiny-pilot/janus-gateway/v1.0.0/COPYING'
    ),

    # JavaScript dependencies.
    LicenseMetadata(
        name='janus.js',
        homepage_url='https://janus.conf.meetecho.com',
        license_glob_pattern='./app/static/third-party/janus-gateway/*/janus.js',
    ),
    LicenseMetadata(
        name='webrtc-adapter',
        homepage_url='https://github.com/webrtcHacks/adapter',
        license_url=
        'https://github.com/webrtcHacks/adapter/blob/18a8b4127cbc1376320cac5742d817b5b7dd0085/LICENSE.md',
    ),
    LicenseMetadata(
        name='socket.io',
        homepage_url='https://socket.io',
        license_url='https://github.com/socketio/socket.io/blob/3.1.2/LICENSE',
    ),

    # Python dependencies, from requirements.txt.
    LicenseMetadata(
        name='eventlet',
        homepage_url='https://eventlet.net',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/eventlet-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='Flask',
        homepage_url='https://flask.palletsprojects.com',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/Flask-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='Flask-SocketIO',
        homepage_url='https://flask-socketio.readthedocs.io',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/Flask_SocketIO-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='Flask-WTF',
        homepage_url='https://flask-wtf.readthedocs.io',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/Flask_WTF-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='pyyaml',
        homepage_url='https://pyyaml.org',
        license_url=
        'https://raw.githubusercontent.com/yaml/pyyaml/5.4.1/LICENSE',
    ),
    LicenseMetadata(
        name='bidict',
        homepage_url='https://bidict.readthedocs.io/en/main',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/bidict-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='click',
        homepage_url='https://palletsprojects.com/p/click',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/click-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='dnspython',
        homepage_url='https://www.dnspython.org',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/dnspython-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='greenlet',
        homepage_url='https://greenlet.readthedocs.io',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/greenlet-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='itsdangerous',
        homepage_url='https://palletsprojects.com/p/itsdangerous/',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/itsdangerous-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='Jinja2',
        homepage_url='https://palletsprojects.com/p/jinja/',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/Jinja2-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='MarkupSafe',
        homepage_url='https://palletsprojects.com/p/markupsafe/',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/MarkupSafe-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='monotonic',
        homepage_url='https://github.com/atdt/monotonic',
        license_url=
        'https://raw.githubusercontent.com/atdt/monotonic/1.5/LICENSE',
    ),
    LicenseMetadata(
        name='python-engineio',
        homepage_url='https://github.com/miguelgrinberg/python-engineio',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/python_engineio-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='python-socketio',
        homepage_url='https://github.com/miguelgrinberg/python-socketio',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/python_socketio-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='six',
        homepage_url='https://github.com/benjaminp/six',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/six-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='Werkzeug',
        homepage_url='https://palletsprojects.com/p/werkzeug/',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/Werkzeug-*.dist-info/LICENSE*',
    ),
    LicenseMetadata(
        name='WTForms',
        homepage_url='https://wtforms.readthedocs.io',
        license_glob_pattern=
        './venv/lib/python3.7/site-packages/WTForms-*.dist-info/LICENSE*',
    ),

    # Ansible dependencies that are not covered above. They are not available
    # permanently on the device because we only create ephemeral Ansible install
    # environments.
    LicenseMetadata(
        name='Ansible',
        homepage_url='https://www.ansible.com',
        license_url=
        'https://raw.githubusercontent.com/ansible/ansible/v2.10.7/COPYING'),
    LicenseMetadata(
        name='cffi',
        homepage_url='http://cffi.readthedocs.org/',
        license_url='https://foss.heptapod.net/pypy/cffi/-/raw/v1.15.1/LICENSE'
    ),
    LicenseMetadata(
        name='cryptography',
        homepage_url='https://cryptography.io',
        license_url=
        'https://raw.githubusercontent.com/pyca/cryptography/38.0.1/LICENSE.BSD'
    ),
    LicenseMetadata(
        name='packaging',
        homepage_url='https://github.com/pypa/packaging',
        license_url=
        'https://raw.githubusercontent.com/pypa/packaging/21.3/LICENSE.BSD'),
    LicenseMetadata(
        name='pycparser',
        homepage_url='https://github.com/eliben/pycparser',
        license_url=
        'https://raw.githubusercontent.com/eliben/pycparser/release_v2.21/LICENSE'
    ),
    LicenseMetadata(
        name='pyparsing',
        homepage_url='https://github.com/pyparsing/pyparsing/',
        license_url=
        'https://raw.githubusercontent.com/pyparsing/pyparsing/pyparsing_3.0.9/LICENSE'
    ),

    # Indirect dependencies through Janus.
    LicenseMetadata(
        name='libnice',
        homepage_url='https://gitlab.freedesktop.org/libnice/libnice',
        license_url=
        'https://gitlab.freedesktop.org/libnice/libnice/-/blob/0.1.18/COPYING',
    ),
    LicenseMetadata(
        name='libsrtp',
        homepage_url='https://github.com/cisco/libsrtp',
        license_url='https://github.com/cisco/libsrtp/blob/v2.2.0/LICENSE',
    ),
    LicenseMetadata(
        name='libwebsockets',
        homepage_url='https://libwebsockets.org',
        license_url=
        'https://libwebsockets.org/git/libwebsockets/tree/LICENSE?h=v3.2-stable',
    ),

    # Fonts.
    LicenseMetadata(
        name='Overpass',
        homepage_url='https://overpassfont.org/',
        license_glob_pattern=
        './app/static/third-party/fonts/Overpass-License.txt',
    ),
]

blueprint = flask.Blueprint('licensing', __name__, url_prefix='/licensing')


@blueprint.route('', methods=['GET'])
def all_licensing_get():
    """Retrieves licensing metadata for TinyPilot and its dependencies.

    Returns:
        A JSON-formatted list of licensing information about TinyPilot and its
        third-party dependencies.

        Example:
        [
            {
                "name": "TinyPilot",
                "homepageUrl": "https://tinypilotkvm.com",
                "licenseUrl": "/licensing/TinyPilot/license"
            },
            {
                "name": "uStreamer",
                "homepageUrl": "https://github.com/pikvm/ustreamer",
                "licenseUrl": "/licensing/uStreamer/license"
            },
            ...
        ]
    """
    response = []
    for license_data in _LICENSE_METADATA:
        response.append({
            'name': license_data.name,
            'licenseUrl': f'/licensing/{license_data.name}/license',
            'homepageUrl': license_data.homepage_url,
        })

    return json_response.success(response)


@blueprint.route('/<project>/license', methods=['GET'])
def project_license_get(project):
    """Retrieves the license for a given project.

    Args:
        project: The name of the project's license to retrieve.

    Returns:
        A plaintext response with the license in plaintext if the license is
        available locally, or a redirect to a public URL if the license is not
        available locally.
    """
    project_metadata = _get_project_metadata(project)
    if not project_metadata:
        return flask.make_response('Unknown project', 404)

    if project_metadata.license_url:
        return _make_redirect_response(project_metadata.license_url)

    matches = glob.glob(project_metadata.license_glob_pattern)
    if not matches:
        return flask.make_response('Project license not found', 404)

    license_path = matches[0]
    return _make_plaintext_response(_read_file(license_path))


def _get_project_metadata(project_name):
    for license_data in _LICENSE_METADATA:
        if license_data.name == project_name:
            return license_data
    return None


def _make_plaintext_response(response_body):
    response = flask.make_response(response_body, 200)
    response.mimetype = 'text/plain'
    return response


def _read_file(license_path):
    with open(license_path, encoding='utf-8') as license_file:
        return license_file.read()


def _make_redirect_response(license_url):
    # We intentionally use a 302 temporary redirect, as the license URL will
    # change when software versions change.
    return flask.redirect(license_url, code=302)
