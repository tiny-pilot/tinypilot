import flask

import debug_logs
import hostname
import json_response
import local_system
import request_parsers.errors
import request_parsers.hostname
import request_parsers.settings
import update.launcher
import update.status
import version
import video_settings

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/debugLogs', methods=['GET'])
def debug_logs_get():
    """Returns the TinyPilot debug log as a plaintext HTTP response.

    Returns:
        A text/plain response with the content of the logs in the response body.
    """
    try:
        return flask.Response(debug_logs.collect(), mimetype='text/plain')
    except debug_logs.Error as e:
        return flask.Response('Failed to retrieve debug logs: %s' % str(e),
                              status=500)


@api_blueprint.route('/shutdown', methods=['POST'])
def shutdown_post():
    try:
        local_system.shutdown()
        return json_response.success()
    except local_system.Error as e:
        return json_response.error(str(e)), 200


@api_blueprint.route('/restart', methods=['POST'])
def restart_post():
    try:
        local_system.restart()
        return json_response.success()
    except local_system.Error as e:
        return json_response.error(str(e)), 200


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

    status, error = update.status.get()
    if error:
        return json_response.error(error), 200
    return json_response.success({'status': str(status)})


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
        update.launcher.start_async()
    except update.launcher.AlreadyInProgressError:
        # If an update is already in progress, treat it as success.
        pass
    except update.launcher.Error as e:
        return json_response.error(str(e)), 200
    return json_response.success()


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
        return json_response.success({'version': version.local_version()})
    except version.Error as e:
        return json_response.error(str(e)), 200


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
        return json_response.success({'version': version.latest_version()})
    except version.Error as e:
        return json_response.error(str(e)), 200


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
        return json_response.success({'hostname': hostname.determine()})
    except hostname.Error as e:
        return json_response.error(str(e)), 200


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
        return json_response.success()
    except request_parsers.errors.Error as e:
        return json_response.error('Invalid input: %s' % str(e)), 200
    except hostname.Error as e:
        return json_response.error('Operation failed: %s' % str(e)), 200


@api_blueprint.route('/status', methods=['GET'])
def status_get():
    """Checks the status of TinyPilot.

    This endpoint may be called from all locations, so there is no restriction
    in regards to CORS.

    Returns:
        A JSON string with two keys: success, error.

        Example:
        {
            'success': true,
            'error': null
        }
    """
    response = json_response.success()
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@api_blueprint.route('/settings/video/fps', methods=['GET'])
def settings_video_fps_get():
    video_fps = video_settings.get_fps()
    return json_response.success({'video_fps': video_fps})


@api_blueprint.route('/settings/video/fps', methods=['PUT'])
def settings_video_fps_put():
    try:
        video_fps = request_parsers.settings.parse_video_fps(flask.request)
        video_settings.set_fps(video_fps)
    except request_parsers.errors.InvalidVideoFpsError as e:
        return json_response.error(str(e)), 200
    else:
        return json_response.success({'video_fps': video_fps})


@api_blueprint.route('/settings/video/fps', methods=['DELETE'])
def settings_video_fps_delete():
    video_settings.unset_fps()
    return json_response.success()


@api_blueprint.route('/settings/video/apply', methods=['POST'])
def settings_video_apply_post():
    video_settings.apply()
    return json_response.success()
