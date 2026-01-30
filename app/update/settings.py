"""Manages a TinyPilot update settings file.

This module is a wrapper around the YAML settings file (settings.yml) that
allows TinyPilot code to modify it cleanly.

Typical usage example:

    settings = update_settings.load()
    settings.ustreamer_desired_fps = 15
    update_settings.save(settings)

Note that we consider the use of settings.yml to be deprecated nowadays. The
default place to store settings and configuration is the SQlite database. We
should only add new properties to settings.yml in exceptional cases, such as:
- Settings that are supposed to be manually overridden by users
- Settings that are closely related to already existing legacy settings

Historically, settings.yml was used as we relied on Ansible to manage and
update the device system state. The canonical way for configuration in Ansible
is files in YAML format, so a YAML file was an obvious choice here. This
wrapper module resides in the update package, since settings.yml was only
processed throughout the update process initially. Over time, we also added a
few other settings, which are independent of the update context.
As of mid 2023, we have finished migrating away from Ansible, so there is no
hard requirement for us to continue using the settings.yml file, except for
backwards compatibility with existing TinyPilot installations.
"""

import yaml

import env
import video_service

_SETTINGS_FILE_PATH = env.abs_path_in_home_dir('settings.yml')

# Define default values for user-configurable TinyPilot settings. The YAML data
# in _SETTINGS_FILE_PATH take precedence over these defaults.
_DEFAULTS = {
    'tinypilot_external_port': 80,
    'tinypilot_external_tls_port': 443,
    # Whether TinyPilot manages TLS keys. Users can override this in their
    # settings file if they want to provide their own TLS keys.
    'tinypilot_manage_tls_keys': True,
    'ustreamer_desired_fps': video_service.DEFAULT_MJPEG_FRAME_RATE,
    'ustreamer_edid': video_service.DEFAULT_EDID,
    'ustreamer_quality': video_service.DEFAULT_MJPEG_QUALITY,
    'ustreamer_h264_bitrate': video_service.DEFAULT_H264_BITRATE,
    'janus_stun_server': video_service.DEFAULT_H264_STUN_SERVER,
    'janus_stun_port': video_service.DEFAULT_H264_STUN_PORT,
}


class Error(Exception):
    pass


class LoadSettingsError(Error):
    pass


class SaveSettingsError(Error):
    pass


class Settings:
    """Manages the parameters for the update process in a YAML file.

    For historical/compatibility reasons, the naming of the uStreamer properties
    is not in line with the naming conventions in the code.
    """

    def __init__(self, data):
        # Merge the defaults with data, with data taking precedence.
        self._data = {**_DEFAULTS, **(data if data else {})}

    def as_dict(self):
        return self._data

    @property
    def ustreamer_desired_fps(self):
        return self._data['ustreamer_desired_fps']

    @ustreamer_desired_fps.setter
    def ustreamer_desired_fps(self, value):
        self._data['ustreamer_desired_fps'] = value

    @property
    def ustreamer_quality(self):
        return self._data['ustreamer_quality']

    @ustreamer_quality.setter
    def ustreamer_quality(self, value):
        self._data['ustreamer_quality'] = value

    @property
    def ustreamer_h264_bitrate(self):
        return self._data['ustreamer_h264_bitrate']

    @ustreamer_h264_bitrate.setter
    def ustreamer_h264_bitrate(self, value):
        self._data['ustreamer_h264_bitrate'] = value

    @property
    def janus_stun_server(self):
        return self._data['janus_stun_server']

    @janus_stun_server.setter
    def janus_stun_server(self, value):
        self._data['janus_stun_server'] = value

    @property
    def janus_stun_port(self):
        return self._data['janus_stun_port']

    @janus_stun_port.setter
    def janus_stun_port(self, value):
        self._data['janus_stun_port'] = value


def load():
    """Retrieves the current TinyPilot update settings.

    Parses the contents of settings file and generates a settings object that
    represents the values in the settings file.

    Args:
        None

    Returns:
        A Settings instance of the current update settings.
    """
    try:
        with open(_SETTINGS_FILE_PATH, encoding='utf-8') as settings_file:
            return _from_file(settings_file)
    except FileNotFoundError:
        return Settings(data=None)
    except IOError as e:
        raise LoadSettingsError(
            'Failed to load settings from settings file') from e


def save(settings):
    """Saves a Settings object to the settings file."""
    try:
        with open(_SETTINGS_FILE_PATH, 'w', encoding='utf-8') as settings_file:
            _to_file(settings, settings_file)
    except IOError as e:
        raise SaveSettingsError(
            'Failed to save settings to settings file') from e


def _from_file(settings_file):
    return Settings(yaml.safe_load(settings_file))


def _to_file(settings, settings_file):
    """Writes a Settings object to a file, excluding any default values."""
    # To avoid polluting the settings file with unnecessary default values, we
    # exclude them instead of hard-coding the defaults in the file.
    settings_without_defaults = {}
    for key, value in settings.as_dict().items():
        if (key not in _DEFAULTS) or (value != _DEFAULTS[key]):
            settings_without_defaults[key] = value

    if settings_without_defaults:
        yaml.safe_dump(settings_without_defaults, settings_file)
