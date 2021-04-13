"""Manages a TinyPilot update settings file.

TinyPilot currently manages most settings through Ansible. When TinyPilot
launches ansible, it passes an extra YAML file that controls properties of the
install and configuration. This module is a wrapper around the YAML file that
allows TinyPilot code to modify it cleanly.

Typical usage example:

    settings = update_settings.load()
    settings.tinypilot_repo_branch = '2.1.5'
    update_settings.save(settings)
"""

import os

import yaml

_SETTINGS_FILE_PATH = os.path.expanduser('~/settings.yml')


class Settings:

    def __init__(self, data):
        self._data = data
        if not self._data:
            self._data = {}

    def as_dict(self):
        return self._data

    def update(self, data):
        self._data.update(data)

    # Note: tinypilot_repo_branch is confusingly named. It should really be
    # tinypilot_repo_version, but this class just reflects the names in the
    # TinyPilot Ansible role.
    @property
    def tinypilot_repo_branch(self):
        return self._data['tinypilot_repo_branch']

    @tinypilot_repo_branch.setter
    def tinypilot_repo_branch(self, value):
        """Sets the value of tinypilot_repo_branch in update settings.

        Args:
            value: A string value of a branch or tag name like '2.1.0' or
                'virtual-storage'.
        """
        self._data['tinypilot_repo_branch'] = value

    @property
    def ustreamer_desired_fps(self):
        # Note: We use the get method here with a default value to avoid raising
        # an exception for when the key doesn't yet exist.
        return self._data.get('ustreamer_desired_fps', None)

    @ustreamer_desired_fps.setter
    def ustreamer_desired_fps(self, value):
        self._data['ustreamer_desired_fps'] = value

    @ustreamer_desired_fps.deleter
    def ustreamer_desired_fps(self):
        # Note: We use the pop method here with a default value to avoid raising
        # an exception for when the key doesn't yet exist.
        self._data.pop('ustreamer_desired_fps', None)


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
        with open(_SETTINGS_FILE_PATH) as settings_file:
            return _from_file(settings_file)
    except FileNotFoundError:
        return Settings(data=None)


def save(settings):
    """Saves a Settings object to the settings file."""
    with open(_SETTINGS_FILE_PATH, 'w') as settings_file:
        _to_file(settings, settings_file)


def _from_file(settings_file):
    return Settings(yaml.safe_load(settings_file))


def _to_file(settings, settings_file):
    """Writes a Settings object to a file."""
    if settings.as_dict():
        yaml.safe_dump(settings.as_dict(), settings_file)


def get_video_fps():
    settings = load()
    return settings.ustreamer_desired_fps


def set_video_fps(video_fps):
    settings = load()
    settings.ustreamer_desired_fps = video_fps
    save(settings)


def unset_video_fps():
    settings = load()
    del settings.ustreamer_desired_fps
    save(settings)
