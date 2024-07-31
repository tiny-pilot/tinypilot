import flask

import db.settings
import debug_logs
import execute
import hostname
import json_response
import local_system
import network
import request_parsers.errors
import request_parsers.hostname
import request_parsers.network
import request_parsers.paste
import request_parsers.video_settings
import update.launcher
import update.settings
import update.status
import version
import video_service
from hid import keyboard as fake_keyboard

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
        return flask.Response(f'Failed to retrieve debug logs: {e}', status=500)


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

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        local_system.restart()
        return json_response.success()
    except local_system.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/update', methods=['GET'])
def update_get():
    """Fetches the state of the latest update job.

    Returns:
        On success, a JSON data structure with the following properties:
        status: str describing the status of the job. Can be one of
                ["NOT_RUNNING", "DONE", "IN_PROGRESS"].
        updateError: str of the error that occurred while updating. If no error
                     occurred, then this will be null.

        Example:
        {
            "status": "NOT_RUNNING",
            "updateError": null
        }
    """
    status, error = update.status.get()
    return json_response.success({'status': str(status), 'updateError': error})


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
            "version": "1.2.3-16+7a6c812",
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
        kind: str.
        data: object (of kind-specific structure), or null.

        Example:
        {
            "version": "1.2.3-16+7a6c812",
            "kind": "automatic",
            "data": null
        }

        Returns error object on failure.
    """
    try:
        update_info = version.latest_version()
    except version.Error as e:
        return json_response.error(e), 500

    return json_response.success({
        'version': update_info.version,
        'kind': update_info.kind,
        'data': update_info.data,
    })


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
    """Changes the machine’s hostname.

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


@api_blueprint.route('/network/status', methods=['GET'])
def network_status():
    """Returns the current status of the available network interfaces.

    Returns:
        On success, a JSON data structure with the following properties:
        ethernet: object
        wifi: object
        The object contains the following fields:
        isConnected: bool
        ipAddress: string or null
        macAddress: string or null

        Example:
        {
            "ethernet": {
                "isConnected": true,
                "ipAddress": "192.168.2.41",
                "macAddress": "e4-5f-01-98-65-03"
            },
            "wifi": {
                "isConnected": false,
                "ipAddress": null,
                "macAddress": null
            }
        }
    """
    # In dev mode, return dummy data because attempting to read the actual
    # settings will fail in most non-Raspberry Pi OS environments.
    if flask.current_app.debug:
        return json_response.success({
            'ethernet': {
                'isConnected': True,
                'ipAddress': '192.168.2.8',
                'macAddress': '00-b0-d0-63-c2-26',
            },
            'wifi': {
                'isConnected': False,
                'ipAddress': None,
                'macAddress': None,
            },
        })
    ethernet, wifi = network.determine_network_status()
    return json_response.success({
        'ethernet': {
            'isConnected': ethernet.is_connected,
            'ipAddress': ethernet.ip_address,
            'macAddress': ethernet.mac_address,
        },
        'wifi': {
            'isConnected': wifi.is_connected,
            'ipAddress': wifi.ip_address,
            'macAddress': wifi.mac_address,
        },
    })


@api_blueprint.route('/network/settings/wifi', methods=['GET'])
def network_wifi_get():
    """Returns the current WiFi settings, if present.

    Returns:
        On success, a JSON data structure with the following properties:
        countryCode: string.
        ssid: string.

        Example:
        {
            "countryCode": "US",
            "ssid": "my-network"
        }

        Returns an error object on failure.
    """
    wifi_settings = network.determine_wifi_settings()
    return json_response.success({
        'countryCode': wifi_settings.country_code,
        'ssid': wifi_settings.ssid,
    })


@api_blueprint.route('/network/settings/wifi', methods=['PUT'])
def network_wifi_enable():
    """Enables a wireless network connection.

    Expects a JSON data structure in the request body that contains a country
    code, an SSID, and optionally a password; all as strings. Example:
    {
        "countryCode": "US",
        "ssid": "my-network",
        "psk": "sup3r-s3cr3t!"
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        wifi_settings = request_parsers.network.parse_wifi_settings(
            flask.request)
        network.enable_wifi(wifi_settings)
        return json_response.success()
    except request_parsers.errors.Error as e:
        return json_response.error(e), 400
    except network.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/network/settings/wifi', methods=['DELETE'])
def network_wifi_disable():
    """Disables the WiFi network connection.

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        network.disable_wifi()
        return json_response.success()
    except network.Error as e:
        return json_response.error(e), 500


@api_blueprint.route('/status', methods=['GET'])
def status_get():
    """Checks the status of TinyPilot.

    This endpoint may be called from all locations, so there is no restriction
    in regards to CORS.

    Returns:
        Empty response, which implies the server is up and running.
    """
    response = json_response.success()
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@api_blueprint.route('/settings/video', methods=['GET'])
def settings_video_get():
    """Retrieves the current video settings.

    Returns:
        On success, a JSON data structure with the following properties:
        - streamingMode: string
        - frameRate: int
        - defaultFrameRate: int
        - mjpegQuality: int
        - defaultMjpegQuality: int
        - h264Bitrate: int
        - defaultH264Bitrate: int

        Example of success:
        {
            "streamingMode": "MJPEG",
            "frameRate": 12,
            "defaultFrameRate": 30,
            "mjpegQuality": 80,
            "defaultMjpegQuality": 80,
            "h264Bitrate": 450,
            "defaultH264Bitrate": 5000
        }

        Returns an error object on failure.
    """
    try:
        update_settings = update.settings.load()
    except update.settings.LoadSettingsError as e:
        return json_response.error(e), 500

    streaming_mode = db.settings.Settings().get_streaming_mode().value

    return json_response.success({
        'streamingMode': streaming_mode,
        'frameRate': update_settings.ustreamer_desired_fps,
        'defaultFrameRate': video_service.DEFAULT_FRAME_RATE,
        'mjpegQuality': update_settings.ustreamer_quality,
        'defaultMjpegQuality': video_service.DEFAULT_MJPEG_QUALITY,
        'h264Bitrate': update_settings.ustreamer_h264_bitrate,
        'defaultH264Bitrate': video_service.DEFAULT_H264_BITRATE,
        'h264StunServer': update_settings.janus_stun_server,
        'defaultH264StunServer': video_service.DEFAULT_H264_STUN_SERVER,
        'h264StunPort': update_settings.janus_stun_port,
        'defaultH264StunPort': video_service.DEFAULT_H264_STUN_PORT,
    })


@api_blueprint.route('/settings/video', methods=['PUT'])
def settings_video_put():
    """Saves new video settings.

    Note: for the new settings to come into effect, you need to make a call to
    the /settings/video/apply endpoint afterwards.

    Expects a JSON data structure in the request body that contains the
    following parameters for the video settings:
    - streamingMode: string
    - frameRate: int
    - mjpegQuality: int
    - h264Bitrate: int
    - h264StunServer: string (hostname or IP address), or null
    - h264StunPort: int, or null

    Note that the h264StunServer and h264StunPort parameters must either both be
    present, or both absent.

    Example of request body:
    {
        "streamingMode": "MJPEG",
        "frameRate": 12,
        "mjpegQuality": 80,
        "h264Bitrate": 450,
        "h264StunServer": "stun.example.com",
        "h264StunPort": 3478
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        streaming_mode = \
            request_parsers.video_settings.parse_streaming_mode(flask.request)
        frame_rate = request_parsers.video_settings.parse_frame_rate(
            flask.request)
        mjpeg_quality = request_parsers.video_settings.parse_mjpeg_quality(
            flask.request)
        h264_bitrate = request_parsers.video_settings.parse_h264_bitrate(
            flask.request)
        h264_stun_server, h264_stun_port = \
            request_parsers.video_settings.parse_h264_stun_address(
                flask.request)
    except request_parsers.errors.InvalidVideoSettingError as e:
        return json_response.error(e), 400

    try:
        update_settings = update.settings.load()
    except update.settings.LoadSettingsError as e:
        return json_response.error(e), 500

    update_settings.ustreamer_desired_fps = frame_rate
    update_settings.ustreamer_quality = mjpeg_quality
    update_settings.ustreamer_h264_bitrate = h264_bitrate
    update_settings.janus_stun_server = h264_stun_server
    update_settings.janus_stun_port = h264_stun_port

    # Store the new parameters. Note: we only actually persist anything if *all*
    # values have passed the validation.
    db.settings.Settings().set_streaming_mode(streaming_mode)
    try:
        update.settings.save(update_settings)
    except update.settings.SaveSettingsError as e:
        return json_response.error(e), 500

    return json_response.success()


@api_blueprint.route('/settings/video/apply', methods=['POST'])
def settings_video_apply_post():
    """Applies the current video settings found in the settings file.

    To allow the current video settings to take effect, we restart the video
    streaming services to reread the settings file and reinitialize the stream.

    Returns:
        Empty response.
    """
    video_service.restart()

    return json_response.success()


@api_blueprint.route('/paste', methods=['POST'])
def paste_post():
    """Pastes text onto the target machine.

    Expects a JSON data structure in the request body that contains the
    following parameters:
    - text: string
    - language: string as an IETF language tag

    Example of request body:
    {
        "text": "Hello, World!",
        "language": "en-US"
    }

    Returns:
        Empty response on success, error object otherwise.
    """
    try:
        keystrokes = request_parsers.paste.parse_keystrokes(flask.request)
    except request_parsers.errors.Error as e:
        return json_response.error(e), 400

    keyboard_path = flask.current_app.config.get('KEYBOARD_PATH')
    execute.background_thread(fake_keyboard.send_keystrokes,
                              args=(keyboard_path, keystrokes))

    return json_response.success()
