import flask

from find_files import find as find_files

views_blueprint = flask.Blueprint('views', __name__, url_prefix='')


@views_blueprint.route('/', methods=['GET'])
def index_get():
    return flask.render_template(
        'index.html', custom_elements_files=find_files.custom_elements_files())
