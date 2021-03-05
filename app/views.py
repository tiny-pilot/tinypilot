import flask

from find_files import find as find_files

views_blueprint = flask.Blueprint('views', __name__, url_prefix='')


@views_blueprint.route('/', methods=['GET'])
def index_get():
    return flask.render_template(
        'index.html', custom_elements_files=find_files.custom_elements_files())


# The style guide is for development purpose only, so we don’t ship it to
# end users.
@views_blueprint.route('/styleguide', methods=['GET'])
def styleguide_get():
    if flask.current_app.debug:
        return flask.render_template('styleguide.html')
    return flask.abort(404)


# On a real install, nginx redirects the /stream route to uStreamer, so a real
# user should never hit this route in production. In development, show a fake
# still image to give a better sense of how the TinyPilot UI looks.
@views_blueprint.route('/stream', methods=['GET'])
def stream_get():
    if flask.current_app.debug:
        return flask.send_file('testdata/test-remote-screen.jpg')
    return flask.abort(404)
