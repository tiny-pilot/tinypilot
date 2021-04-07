"""Manages a TinyPilot settings file.

Typical usage example:

with open(update_settings.DEFAULT_SETTINGS_FILE_PATH) as settings_file:
    settings = update_settings.load(settings_file)

settings.tinypilot_repo_branch = '2.1.5'

with open(update_settings.DEFAULT_SETTINGS_FILE_PATH, 'w') as settings_file:
    update_settings.save(settings, settings_file)
"""

import os

import yaml

DEFAULT_SETTINGS_FILE_PATH = os.path.expanduser('~/settings.yml')


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


def load(settings_file):
    """Create a settings instance to manage the TinyPilot settings file.

    Parses the contents of settings file and generates a settings object that
    represents the values in the settings file.

    Args:
        settings_file: File containing TinyPilot settings in YAML format.

    Returns:
        An object containing TinyPilot settings.
    """
    return Settings(yaml.safe_load(settings_file))


def save(settings, settings_file):
    """Writes the current settings to the settings file."""
    if settings.as_dict():
        yaml.safe_dump(settings.as_dict(), settings_file)


def get_settings():
    """Get the current Settings object from the default settings file."""

    try:
        with open(DEFAULT_SETTINGS_FILE_PATH) as settings_file:
            settings = load(settings_file)
    except FileNotFoundError:
        settings = Settings(data=None)
    return settings


def save_settings(settings):
    """Save the Settings object to the default settings file."""

    with open(DEFAULT_SETTINGS_FILE_PATH, 'w') as settings_file:
        save(settings, settings_file)
