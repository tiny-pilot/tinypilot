import flask

import local_system
import update

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/shutdown', methods=['POST'])
def shutdown_post():
    try:
        local_system.shutdown()
        return _json_success()
    except local_system.Error as e:
        return _json_error(str(e)), 500


@api_blueprint.route('/restart', methods=['POST'])
def restart_post():
    try:
        local_system.restart()
        return _json_success()
    except local_system.Error as e:
        return _json_error(str(e)), 500


@api_blueprint.route('/version', methods=['GET'])
def version_get():
    try:
        version = update.version()
        return _json_success({"version": version})
    except update.Error as e:
        return _json_error(str(e)), 500


@api_blueprint.route('/latestRelease', methods=['GET'])
def latest_release_get():
    try:
        latest_release = update.latest_release()
        return _json_success({"latestRelease": latest_release})
    except update.Error as e:
        return _json_error(str(e)), 500


@api_blueprint.route('/update', methods=['POST'])
def update_post():
    try:
        update.update()
        return _json_success()
    except update.Error as e:
        return _json_error(str(e)), 500


def _json_success(fields={}):
    response = {
        'success': True,
        'error': None,
    }
    for k, v in fields.items():
        response[k] = v
    return flask.jsonify(response)


def _json_error(message):
    return flask.jsonify({
        'success': False,
        'error': message,
    })
