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

import video_settings

_SETTINGS_FILE_PATH = os.path.expanduser('~/settings.yml')


class Error(Exception):
    pass


class LoadSettingsError(Error):
    pass


class SaveSettingsError(Error):
    pass


class Settings:
    """Manages the parameters for the update process in a YAML file.

    Note: To avoid polluting the settings file with unnecessary default values,
    we unset them instead of hard-coding the defaults in the file.
    """

    def __init__(self, data):
        self._data = data
        if not self._data:
            self._data = {}

    def as_dict(self):
        return self._data

    @property
    def ustreamer_desired_fps(self):
        return self._get_or_default('ustreamer_desired_fps',
                                    video_settings.DEFAULT_FPS)

    @ustreamer_desired_fps.setter
    def ustreamer_desired_fps(self, value):
        self._set_or_clear('ustreamer_desired_fps', value,
                           video_settings.DEFAULT_FPS)

    @property
    def ustreamer_quality(self):
        return self._get_or_default('ustreamer_quality',
                                    video_settings.DEFAULT_JPEG_QUALITY)

    @ustreamer_quality.setter
    def ustreamer_quality(self, value):
        self._set_or_clear('ustreamer_quality', value,
                           video_settings.DEFAULT_JPEG_QUALITY)

    @property
    def ustreamer_h264_bitrate(self):
        return self._get_or_default('ustreamer_h264_bitrate',
                                    video_settings.DEFAULT_H264_BITRATE)

    @ustreamer_h264_bitrate.setter
    def ustreamer_h264_bitrate(self, value):
        self._set_or_clear('ustreamer_h264_bitrate', value,
                           video_settings.DEFAULT_H264_BITRATE)

    def _set_or_clear(self, prop_name, value, default_value):
        if value == default_value:
            if prop_name in self._data:
                del self._data[prop_name]
            return

        self._data[prop_name] = value

    def _get_or_default(self, prop_name, default_value):
        if prop_name in self._data:
            return self._data[prop_name]
        return default_value


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
    """Writes a Settings object to a file."""
    if settings.as_dict():
        yaml.safe_dump(settings.as_dict(), settings_file)
