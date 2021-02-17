import flask

import debug_logs
import git
import hostname
import local_system
import request_parsers.errors
import request_parsers.hostname
import update

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/debugLogs', methods=['GET'])
def debug_logs_get():
    """Returns the TinyPilot debug log as a plaintext HTTP response.

    Returns:
        A text/plain response with the content of the logs in the response body.
    """
    try:
        return flask.Response(debug_logs.collect())
    except debug_logs.Error as e:
        return flask.Response('Failed to retrieve debug logs: %s' % str(e),
                              status=500)


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


@api_blueprint.route('/update', methods=['GET'])
def update_get():
    """Fetches the state of the latest update job.

    Returns:
        A JSON string describing the latest update job.

        success: true if we were able to fetch job.
        error: null if successful, str otherwise.
        status: str describing the status of the job. Can be one of
                ["NOT_RUNNING", "DONE", "IN_PROGRESS"].
    """

    status, error = update.get_current_state()
    if error:
        return _json_error(error), 200
    return _json_success({'status': str(status)})


@api_blueprint.route('/update', methods=['PUT'])
def update_put():
    """Initiates job to update TinyPilot to the latest version available.

    This endpoint asynchronously starts a job to update TinyPilot to the latest
    version.  API clients can then query the status of the job with GET
    /api/update to see the status of the update.

    Returns:
        A JSON string with two keys: success and error.

        success: true if update task was initiated successfully.
        error: null if successful, str otherwise.
    """
    try:
        update.start_async()
    except update.AlreadyInProgressError:
        # If an update is already in progress, treat it as success.
        pass
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
        return _json_success({'version': git.local_head_commit_id()})
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
        return _json_success({'version': git.remote_head_commit_id()})
    except git.Error as e:
        return _json_error(str(e)), 200


@api_blueprint.route('/hostname', methods=['GET'])
def hostname_get():
    """Determines the hostname of the machine.

    Returns:
        A JSON string with three keys when successful and two otherwise:
        success, error and hostname (if successful).

        success: true if successful.
        error: null if successful, str otherwise.
        hostname: str if successful.

        Example of success:
        {
            'success': true,
            'error': null,
            'hostname': 'tinypilot'
        }
        Example of error:
        {
            'success': false,
            'error': 'Cannot determine hostname.'
        }
    """
    try:
        return _json_success({'hostname': hostname.determine()})
    except hostname.Error as e:
        return _json_error(str(e)), 200


@api_blueprint.route('/hostname', methods=['PUT'])
def hostname_set():
    """Changes the machine’s hostname

    Expects a JSON data structure in the request body that contains the
    new hostname as string. Example:
    {
        'hostname': 'grandpilot'
    }

    Returns:
        A JSON string with two keys: success, error.

        success: true if successful.
        error: null if successful, str otherwise.

        Example of success:
        {
            'success': true,
            'error': null
        }
        Example of error:
        {
            'success': false,
            'error': 'Invalid hostname.'
        }
    """
    try:
        new_hostname = request_parsers.hostname.parse_hostname(flask.request)
        hostname.change(new_hostname)
        return _json_success()
    except request_parsers.errors.Error as e:
        return _json_error('Malformed request: %s' % str(e)), 200
    except hostname.Error as e:
        return _json_error('Operation failed: %s' % str(e)), 200


# The default dictionary is okay because we're not modifying it.
# pylint: disable=dangerous-default-value
def _json_success(fields={}):
    response = {
        'success': True,
        'error': None,
    }
    for key, val in fields.items():
        response[key] = val
    return flask.jsonify(response)


def _json_error(message):
    return flask.jsonify({
        'success': False,
        'error': message,
    })
