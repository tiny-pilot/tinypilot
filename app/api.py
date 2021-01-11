import logging
import subprocess

import flask

import git
import local_system

logger = logging.getLogger(__name__)
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


@api_blueprint.route('/update', methods=['POST'])
def update_post():
    """API endpoint that updates Tinypilot via its update script.

    The script lives in /opt/tinypilot-privileged/update and is called via the
    subprocess module.

    Returns:
        returns _json_success(), which is a simple:
        {
            'success': true,
            'error': null,
        }
        indicating that it worked.

    Raises:
        If the return code of the result is not 0, a CalledProcessError will
        be raised. After caught, the stderr part of the result of passed to
        _json_error, which will return something like this, for example:
        {
            'success': false,
            'error': 'sudo: /opt/tinypilot-privileged/update: command not found'
        }
    """
    logger.info('Updating TinyPilot')
    result = subprocess.run(['sudo', '/opt/tinypilot-privileged/update'],
                            capture_output=True,
                            text=True)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        return _json_error(result.stderr.strip()), 500
    return _json_success()


@api_blueprint.route('/version', methods=['GET'])
def version_get():
    """API endpoint that returns the local HEAD commit ID.

    See git.local_head_commit_id().

    Returns:
        returns _json_success with the local HEAD commit ID, for example:
        {
            'success': true,
            'error': null,
            'version': 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05',
        }

    Raises:
        If the return code of the result is not 0, a git.Error will be raised,
        for example:
        {
            'success': false,
            'error': 'git rev-parse HEAD failed.',
        }
    """
    try:
        return _json_success({"version": git.local_head_commit_id()})
    except git.Error as e:
        return _json_error(str(e)), 500


@api_blueprint.route('/latestRelease', methods=['GET'])
def latest_release_get():
    """API endpoint that returns the origin/master HEAD commit ID.

    See git.remote_head_commit_id().

    Returns:
        returns _json_success with the origin/master HEAD commit ID, for example:
        {
            'success': true,
            'error': null,
            'version': 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05',
        }

    Raises:
        If the return code of the result is not 0, a git.Error will be raised,
        for example:
        {
            'success': false,
            'error': 'git rev-parse origin/master failed.',
        }
        or
        {
            'success': false,
            'error': 'git fetch failed.',
        }
    """
    try:
        return _json_success({"version": git.remote_head_commit_id()})
    except git.Error as e:
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
