import flask

import db.settings
import hostname
from find_files import find as find_files

views_blueprint = flask.Blueprint('views', __name__, url_prefix='')

# Default hostname of TinyPilot device.
_DEFAULT_HOSTNAME = 'tinypilot'


@views_blueprint.route('/', methods=['GET'])
def index_get():
    # TODO(jotaen) While H264 is being worked on, we still rely on the legacy
    #              mechanism to determine the remote screen mode. Once we are
    #              done, we abandon the `USE_WEBRTC_REMOTE_SCREEN` config.
    use_webrtc = flask.current_app.config.get('USE_WEBRTC_REMOTE_SCREEN', False)
    if flask.current_app.debug:
        use_webrtc = db.settings.Settings().get_streaming_mode(
        ) == db.settings.StreamingMode.H264

    return flask.render_template(
        'index.html',
        use_webrtc_remote_screen=use_webrtc,
        page_title_prefix=_page_title_prefix(),
        custom_elements_files=find_files.custom_elements_files())


# The style guide is for development purpose only, so we don’t ship it to
# end users.
@views_blueprint.route('/styleguide', methods=['GET'])
def styleguide_get():
    if flask.current_app.debug:
        return flask.render_template(
            'styleguide.html',
            custom_elements_files=find_files.custom_elements_files())
    return flask.abort(404)


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
