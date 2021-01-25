import flask

import debug_logs
import git
import local_system
import update

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/debugLogs', methods=['GET'])
def fetch_debug_logs():
    """Runs the collect-debug-logs script and returns the output to the user.

    Returns:
        A text/plain response with the content of the logs in the response body.
    """
    try:
        return flask.Response(debug_logs.collect())
    except debug_logs.Error as e:
        return flask.Response(
            'Failed to retrieve debug logs: %s' % str(e),
            status=flask.status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_blueprint.route('/shutdown', methods=['POST'])
def shutdown_post():
    try:
        local_system.shutdown()
        return _json_success()
    except local_system.Error as e:
        return _json_error(str(e)), 200


@api_blueprint.route('/restart', methods=['POST'])
def restart_post():
    try:
        local_system.restart()
        return _json_success()
    except local_system.Error as e:
        return _json_error(str(e)), 200


@api_blueprint.route('/update', methods=['POST'])
def update_post():
    """Updates TinyPilot to the latest version available.

    This is a slow endpoint, as it is expected to take 2~4 minutes to
    complete.

    Returns:
        A JSON string with two keys: success and error.

        success: true if successful.
        error: null if successful, str otherwise.

        Example of success:
        {
            'success': true,
            'error': null,
        }
        Example of error:
        {
            'success': false,
            'error': 'sudo: /opt/tinypilot-privileged/update: command not found'
        }
    """
    try:
        update.update()
    except update.Error as e:
        return _json_error(str(e)), 200
    return _json_success()


@api_blueprint.route('/version', methods=['GET'])
def version_get():
    """Retrieves the current installed version of TinyPilot.

    Returns:
        A JSON string with three keys when successful and two otherwise:
        success, error and version (if successful).

        success: true if successful.
        error: null if successful, str otherwise.
        version: str.

        Example of success:
        {
            'success': true,
            'error': null,
            'version': 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05',
        }
        Example of error:
        {
            'success': false,
            'error': 'git rev-parse HEAD failed.',
        }
    """
    try:
        return _json_success({"version": git.local_head_commit_id()})
    except git.Error as e:
        return _json_error(str(e)), 200


@api_blueprint.route('/latestRelease', methods=['GET'])
def latest_release_get():
    """Retrieves the latest version of TinyPilot.

    Returns:
        A JSON string with three keys when successful and two otherwise:
        success, error and version (if successful).

        success: true if successful.
        error: null if successful, str otherwise.
        version: str.

        Example of success:
        {
            'success': true,
            'error': null,
            'version': 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05',
        }
        Example of error:
        {
            'success': false,
            'error': 'git rev-parse origin/master failed.',
        }
    """
    try:
        return _json_success({"version": git.remote_head_commit_id()})
    except git.Error as e:
        return _json_error(str(e)), 200


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
