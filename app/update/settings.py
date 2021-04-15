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


class Settings:

    def __init__(self, data):
        self._data = data
        if not self._data:
            self._data = {}

    def as_dict(self):
        return self._data

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
        with open(_settings_file_path()) as settings_file:
            return _from_file(settings_file)
    except FileNotFoundError:
        return Settings(data=None)


def save(settings):
    """Saves a Settings object to the settings file."""
    with open(_settings_file_path(), 'w') as settings_file:
        _to_file(settings, settings_file)


def _from_file(settings_file):
    return Settings(yaml.safe_load(settings_file))


def _to_file(settings, settings_file):
    """Writes a Settings object to a file."""
    if settings.as_dict():
        yaml.safe_dump(settings.as_dict(), settings_file)


# This could be a constant, but we're doing it as a function so that we can mock
# out the os.path.expanduser call for unit testing.
def _settings_file_path():
    return os.path.expanduser('~/settings.yml')
