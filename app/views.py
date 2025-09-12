import functools
import urllib.parse

import flask

import auth
import db.settings
import hostname
import session
import update.settings
from find_files import find as find_files

views_blueprint = flask.Blueprint('views', __name__, url_prefix='')

# Default hostname of TinyPilot device.
_DEFAULT_HOSTNAME = 'tinypilot'


def require_authentication(func):

    @functools.wraps(func)
    def decorated_function(*args, **kwargs):
        if not session.is_auth_valid():
            response = flask.redirect('/login' + _login_redirect_query())
            # Prevent Flask from converting the redirect location into an
            # absolute URL. This generates incorrect results, since we are
            # sitting behind a proxy.
            response.autocorrect_location_header = False
            return response
        return func(*args, **kwargs)

    return decorated_function


@views_blueprint.route('/', methods=['GET'])
@require_authentication
def index_get():
    use_webrtc = db.settings.Settings().get_streaming_mode(
    ) == db.settings.StreamingMode.H264

    try:
        update_settings = update.settings.load()
    except update.settings.LoadSettingsError:
        return flask.abort(500)

    return flask.render_template(
        'index.html',
        is_debug=flask.current_app.debug,
        use_webrtc_remote_screen=use_webrtc,
        janus_stun_server=update_settings.janus_stun_server,
        janus_stun_port=update_settings.janus_stun_port,
        page_title_prefix=_page_title_prefix(),
        is_standalone_mode=_is_standalone_mode(),
        custom_elements_files=find_files.custom_elements_files(),
        requires_authentication=auth.is_authentication_required(),
    )


@views_blueprint.route('/login', methods=['GET'])
def login_get():
    if session.is_auth_valid():
        return flask.redirect('/')
    return flask.render_template('login.html',
                                 page_title_prefix=_page_title_prefix())


# The style guide is for development purpose only, so we don’t ship it to
# end users.
@views_blueprint.route('/styleguide', methods=['GET'])
def styleguide_get():
    if flask.current_app.debug:
        return flask.render_template(
            'styleguide.html',
            custom_elements_files=find_files.custom_elements_files())
    return flask.abort(404)


@views_blueprint.route('/dedicated-window-placeholder', methods=['GET'])
def dedicated_window_placeholder_get():
    return flask.render_template('dedicated-window-placeholder.html',
                                 page_title_prefix=_page_title_prefix())


# On a real install, nginx redirects the /stream route to uStreamer, so a real
# user should never hit this route in production. In development, show a fake
# still image to give a better sense of how the TinyPilot UI looks.
@views_blueprint.route('/stream', methods=['GET'])
def stream_get():
    if flask.current_app.debug:
        return flask.send_file('testdata/test-remote-screen.jpg')
    return flask.abort(404)


def _page_title_prefix():
    if hostname.determine().lower() != _DEFAULT_HOSTNAME.lower():
        return f'{hostname.determine()} - '
    return ''


def _is_standalone_mode():
    return flask.request.args.get('viewMode') == 'standalone'


def _login_redirect_query():
    # `flask.request.full_path` always carries a trailing `?`. This doesn’t
    # harm, but it’s a bit unaesthetic. Therefore, we trim/clean the path.
    # For similar reasons, we also only append the `?redirect` parameter if
    # the current path differs from the default one (`/`).
    full_path = urllib.parse.urlsplit(flask.request.full_path).geturl()
    if full_path == '/':
        return ''
    return '?redirect=' + urllib.parse.quote_plus(full_path)
