from datetime import datetime

import flask

import git
import local_system
import update

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


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
    """Fetch the state of the latest update job.

    Returns:
        A JSON string describing the latest update job.

        success: true if we were able to fetch job.
        error: null if successful, str otherwise.
        status: str describing the status of the job
        startTime: start time of the job
        endTime: end time of the job if job finished, null otherwise
    """

    def format_timestamp(timestamp):
        if timestamp is None:
            return None
        return datetime.fromtimestamp(timestamp).isoformat()

    def make_response(job, status):
        return _json_success({
            'status': status,
            'startTime': job and format_timestamp(job.start_time),
            'endTime': job and format_timestamp(job.end_time),
        })

    job = update.current_job
    if job is None:
        return make_response(None, "No update in progress")

    status = job.get_status()
    if status == job.Status.PENDING:
        return make_response(job, "Updating")

    # Update job finished (not pending), unset the global variable.
    update.current_job = None

    if status == job.Status.DONE:
        return make_response(job, "Update complete")
    if status == job.Status.TIMEOUT:
        return _json_success(job, "Update timed out.")
    if status == job.Status.ERROR:
        return _json_error("Update job failed: %s" % job.error)
    return _json_error("Update job is in an unrecognized state.")


@api_blueprint.route('/update', methods=['PUT'])
def update_put():
    """Initiates job to update TinyPilot to the latest version available.
    This is a slow endpoint, as it is expected to take 2~4 minutes to
    complete. The status of the job can be fetched with GET /api/update.

    Returns:
        A JSON string with two keys: success and error.

        success: true if update job was successful.
        error: null if successful, str otherwise.
    """
    if update.current_job is not None:
        status = update.current_job.get_status()
        if status == update.Status.PENDING:
            return _json_error("An update is already in progreses"), 200

    try:
        job = update.UpdateJob()
    except update.Error as e:
        return _json_error("Failed to initiate update: %s", str(e)), 200

    update.current_job = job
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
