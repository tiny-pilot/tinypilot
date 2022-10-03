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

_SETTINGS_FILE_PATH = os.path.expanduser('~/settings.yml')


class Error(Exception):
    pass


class LoadSettingsError(Error):
    pass


class SaveSettingsError(Error):
    pass


class Settings:

    def __init__(self, data):
        self._data = data
        if not self._data:
            self._data = {}

    def as_dict(self):
        return self._data

    @property
    def ustreamer_desired_fps(self):
        return self._data.get('ustreamer_desired_fps', None)

    @ustreamer_desired_fps.setter
    def ustreamer_desired_fps(self, value):
        self._data['ustreamer_desired_fps'] = value

    @ustreamer_desired_fps.deleter
    def ustreamer_desired_fps(self):
        if 'ustreamer_desired_fps' in self._data:
            del self._data['ustreamer_desired_fps']

    @property
    def ustreamer_quality(self):
        return self._data.get('ustreamer_quality', None)

    @ustreamer_quality.setter
    def ustreamer_quality(self, value):
        self._data['ustreamer_quality'] = value

    @ustreamer_quality.deleter
    def ustreamer_quality(self):
        if 'ustreamer_quality' in self._data:
            del self._data['ustreamer_quality']

    def set_h264_status(self, is_enabled):
        if is_enabled:
            self._data['ustreamer_h264_sink'] = 'tinypilot::ustreamer::h264'
            self._data['ustreamer_h264_sink_mode'] = 777
            self._data['ustreamer_h264_sink_rm'] = True
        else:
            if 'ustreamer_h264_sink' in self._data:
                del self._data['ustreamer_h264_sink']
            if 'ustreamer_h264_sink_mode' in self._data:
                del self._data['ustreamer_h264_sink_mode']
            if 'ustreamer_h264_sink_rm' in self._data:
                del self._data['ustreamer_h264_sink_rm']

    def is_h264_enabled(self):
        return (self._data.get('ustreamer_h264_sink',
                               None) == 'tinypilot::ustreamer::h264' and
                self._data.get('ustreamer_h264_sink_mode', None) == 777 and
                self._data.get('ustreamer_h264_sink_rm', None) is True)


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
