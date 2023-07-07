"""Manages a TinyPilot update settings file.

TinyPilot currently manages most settings through Ansible. When TinyPilot
launches ansible, it passes an extra YAML file that controls properties of the
install and configuration. This module is a wrapper around the YAML file that
allows TinyPilot code to modify it cleanly.

Typical usage example:

    settings = update_settings.load()
    settings.ustreamer_desired_fps = 15
    update_settings.save(settings)
"""

import os

import yaml

import video_service

_SETTINGS_FILE_PATH = os.path.expanduser('~/settings.yml')

# Define constant values of the TinyPilot system. These constants take
# precedence over the YAML data in _SETTINGS_FILE_PATH and _DEFAULTS. These
# values are not user-configurable.
_CONSTANTS = {
    'ustreamer_interface':
        '127.0.0.1',  # Must match ansible-role/vars/main.yml.
    'ustreamer_port': 8001,  # Must match ansible-role/vars/main.yml.
}

# Define default values for user-configurable TinyPilot settings. The YAML data
# in _SETTINGS_FILE_PATH take precedence over these defaults.
_DEFAULTS = {
    'tinypilot_keyboard_interface': '/dev/hidg0',
    'tinypilot_mouse_interface': '/dev/hidg1',
    'ustreamer_desired_fps': video_service.DEFAULT_FRAME_RATE,
    'ustreamer_quality': video_service.DEFAULT_MJPEG_QUALITY,
    'ustreamer_h264_bitrate': video_service.DEFAULT_H264_BITRATE,
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
        # Merge defaults, data, and constants, where constants take the
        # highest precedence.
        self._data = {**_DEFAULTS, **(data if data else {}), **_CONSTANTS}

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


def load():
    """Retrieves the current TinyPilot update settings

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
    """Writes a Settings object to a file, excluding any constants or defaults.
    """
    # To avoid polluting the settings file with unnecessary default or constant
    # values, we exclude them instead of hard-coding their values in the file.
    settings_without_constants_or_defaults = {}
    for key, value in settings.as_dict().items():
        if (key in _CONSTANTS) or (key in _DEFAULTS and
                                   value == _DEFAULTS[key]):
            continue
        settings_without_constants_or_defaults[key] = value

    if settings_without_constants_or_defaults:
        yaml.safe_dump(settings_without_constants_or_defaults, settings_file)
