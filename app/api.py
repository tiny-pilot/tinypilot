import flask

import debug_logs
import hostname
import json_response
import local_system
import request_parsers.errors
import request_parsers.hostname
import request_parsers.video_settings
import update.launcher
import update.settings
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
    """Triggers shutdown of the system.

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        local_system.shutdown()
        return json_response.success()
    except local_system.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/restart', methods=['POST'])
def restart_post():
    """Triggers restart of the system.

    For backwards compatibility, we must include the now deprecated `success`
    and `error` properties in the response. This is needed for when TinyPilot
    updates from a version before our migration to using conventional HTTP
    status codes. Issue: https://github.com/tiny-pilot/tinypilot/issues/506

    Returns:
        No additional properties on success.

        success: true for backwards compatibility.
        error: null for backwards compatibility.

        Returns error object otherwise.
    """
    try:
        local_system.restart()
        return json_response.success({'success': True, 'error': None})
    except local_system.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/update', methods=['GET'])
def update_get():
    """Fetches the state of the latest update job.

    For backwards compatibility, we must include the now deprecated `success`
    and `error` properties in the response. This is needed for when TinyPilot
    updates from a version before our migration to using conventional HTTP
    status codes. Issue: https://github.com/tiny-pilot/tinypilot/issues/506

    Returns:
        On success, a JSON data structure with the following properties:
        status: str describing the status of the job. Can be one of
                ["NOT_RUNNING", "DONE", "IN_PROGRESS"].
        updateError: str of the error that occured while updating. If no error
                     occured, then this will be null.
        success: true for backwards compatibility.
        error: null for backwards compatibility.

        Example:
        {
            "status": "NOT_RUNNING",
            "updateError": null,
            "success": true,
            "error": null
        }
    """

    status, error = update.status.get()
    return json_response.success({
        'status': str(status),
        'updateError': error,
        'success': True,
        'error': None
    })


@api_blueprint.route('/update', methods=['PUT'])
def update_put():
    """Initiates job to update TinyPilot to the latest version available.

    This endpoint asynchronously starts a job to update TinyPilot to the latest
    version.  API clients can then query the status of the job with GET
    /api/update to see the status of the update.

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        update.launcher.start_async()
    except update.launcher.AlreadyInProgressError:
        # If an update is already in progress, treat it as success.
        pass
    except update.launcher.Error as e:
        return json_response.error(e), 500
    return json_response.success()


@api_blueprint.route('/version', methods=['GET'])
def version_get():
    """Retrieves the current installed version of TinyPilot.

    Returns:
        On success, a JSON data structure with the following properties:
        version: str.

        Example:
        {
            "version": "bf07bfe72941457cf068ca0a44c6b0d62dd9ef05",
        }

        Returns error object on failure.
    """
    try:
        return json_response.success({'version': version.local_version()})
    except version.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/latestRelease', methods=['GET'])
def latest_release_get():
    """Retrieves the latest version of TinyPilot.

    Returns:
        On success, a JSON data structure with the following properties:
        version: str.

        Example:
        {
            "version": "bf07bfe72941457cf068ca0a44c6b0d62dd9ef05",
        }

        Returns error object on failure.
    """
    try:
        return json_response.success({'version': version.latest_version()})
    except version.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/hostname', methods=['GET'])
def hostname_get():
    """Determines the hostname of the machine.

    Returns:
        On success, a JSON data structure with the following properties:
        hostname: string.

        Example:
        {
            "hostname": "tinypilot"
        }

        Returns an error object on failure.
    """
    try:
        return json_response.success({'hostname': hostname.determine()})
    except hostname.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/hostname', methods=['PUT'])
def hostname_set():
    """Changes the machine’s hostname

    Expects a JSON data structure in the request body that contains the
    new hostname as string. Example:
    {
        "hostname": "grandpilot"
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        new_hostname = request_parsers.hostname.parse_hostname(flask.request)
        hostname.change(new_hostname)
        return json_response.success()
    except request_parsers.errors.Error as e:
        return json_response.error(e), 400
    except hostname.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/status', methods=['GET'])
def status_get():
    """Checks the status of TinyPilot.

    This endpoint may be called from all locations, so there is no restriction
    in regards to CORS.

    For backwards compatibility, we must include the now deprecated `success`
    and `error` properties in the response. This is needed for when TinyPilot
    updates from a version before our migration to using conventional HTTP
    status codes. Issue: https://github.com/tiny-pilot/tinypilot/issues/506

    Returns:
        No additional properties implies the server is up and running.

        success: true for backwards compatibility.
        error: null for backwards compatibility.
    """
    response = json_response.success({'success': True, 'error': None})
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@api_blueprint.route('/settings/video/fps', methods=['GET'])
def settings_video_fps_get():
    """Retrieves the current video FPS setting.

    Returns:
        On success, a JSON data structure with the following properties:
        videoFps: int.

        Example of success:
        {
            "videoFps": 30
        }

        Returns an error object on failure.
    """
    try:
        video_fps = update.settings.load().ustreamer_desired_fps
    except update.settings.LoadSettingsError as e:
        return json_response.error(e), 200
    # Note: Default values are not set in the settings file. So when the
    # values are unset, we must respond with the correct default value.
    if video_fps is None:
        video_fps = video_settings.DEFAULT_FPS
    return json_response.success({'videoFps': video_fps})


@api_blueprint.route('/settings/video/fps', methods=['PUT'])
def settings_video_fps_put():
    """Changes the current video FPS setting.

    Expects a JSON data structure in the request body that contains the
    new videoFps as an integer. Example:
    {
        "videoFps": 30
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        video_fps = request_parsers.video_settings.parse_fps(flask.request)
        settings = update.settings.load()
        # Note: To avoid polluting the settings file with unnecessay default
        # values, we unset them instead.
        if video_fps == video_settings.DEFAULT_FPS:
            del settings.ustreamer_desired_fps
        else:
            settings.ustreamer_desired_fps = video_fps
        update.settings.save(settings)
    except request_parsers.errors.InvalidVideoFpsError as e:
        return json_response.error(e), 400
    except update.settings.SaveSettingsError as e:
        return json_response.error(e), 500
    return json_response.success()


@api_blueprint.route('/settings/video/fps/default', methods=['GET'])
def settings_video_fps_default_get():
    """Retrieves the default video FPS setting.

    Returns:
        On success, a JSON data structure with the following properties:
        videoFps: int.

        Example of success:
        {
            "videoFps": 30
        }
    """
    return json_response.success({'videoFps': video_settings.DEFAULT_FPS})


@api_blueprint.route('/settings/video/jpeg_quality', methods=['GET'])
def settings_video_jpeg_quality_get():
    """Retrieves the current video JPEG quality setting.

    Returns:
        On success, a JSON data structure with the following properties:
        videoJpegQuality: int.

        Example:
        {
            "videoJpegQuality": 80
        }

        Returns an error object on failure.
    """
    try:
        video_jpeg_quality = update.settings.load().ustreamer_quality
    except update.settings.LoadSettingsError as e:
        return json_response.error(e), 500
    # Note: Default values are not set in the settings file. So when the
    # values are unset, we must respond with the correct default value.
    if video_jpeg_quality is None:
        video_jpeg_quality = video_settings.DEFAULT_JPEG_QUALITY
    return json_response.success({'videoJpegQuality': video_jpeg_quality})


@api_blueprint.route('/settings/video/jpeg_quality', methods=['PUT'])
def settings_video_jpeg_quality_put():
    """Changes the current video JPEG quality setting.

    Expects a JSON data structure in the request body that contains the
    new videoJpegQuality as an integer. Example:
    {
        "videoJpegQuality": 80
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        video_jpeg_quality = request_parsers.video_settings.parse_jpeg_quality(
            flask.request)
        settings = update.settings.load()
        # Note: To avoid polluting the settings file with unnecessay default
        # values, we unset them instead.
        if video_jpeg_quality == video_settings.DEFAULT_JPEG_QUALITY:
            del settings.ustreamer_quality
        else:
            settings.ustreamer_quality = video_jpeg_quality
        update.settings.save(settings)
    except request_parsers.errors.InvalidVideoJpegQualityError as e:
        return json_response.error(e), 400
    except update.settings.SaveSettingsError as e:
        return json_response.error(e), 500
    return json_response.success()


@api_blueprint.route('/settings/video/jpeg_quality/default', methods=['GET'])
def settings_video_jpeg_quality_default_get():
    """Retrieves the default video JPEG quality setting.

    Returns:
        On success, a JSON data structure with the following properties:
        videoJpegQuality: int.

        Example:
        {
            "videoJpegQuality": 80
        }
    """
    return json_response.success(
        {'videoJpegQuality': video_settings.DEFAULT_JPEG_QUALITY})


@api_blueprint.route('/settings/video/apply', methods=['POST'])
def settings_video_apply_post():
    """Applies the current video settings found in the settings file.

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        video_settings.apply()
    except video_settings.Error as e:
        return json_response.error(e), 500
    return json_response.success()
