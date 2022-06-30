import flask

import git


class Error(Exception):
    pass


class GitError(Error):
    pass


class VersionFileError(Error):
    pass


_VERSION_FILE = './VERSION'


def _is_debug():
    return flask.current_app.debug


def local_version():
    """Read the current local version string from the version file.

    If run locally, in development, where a version file is not present then a
    dummy version string is returned.

    Returns:
        A version string.

    Raises:
        VersionFileError: If an error occurred while accessing the version file.
    """
    if _is_debug():
        return '0000000'

    try:
        with open(_VERSION_FILE, encoding='utf-8') as file:
            version = file.read().strip()
    except (IOError, UnicodeDecodeError) as e:
        raise VersionFileError('Failed to check local version: %s' %
                               str(e)) from e
    if version == '':
        raise VersionFileError('The local version file cannot be empty.')
    return version


def latest_version():
    try:
        return git.remote_head_commit_id()
    except git.Error as e:
        raise GitError('Failed to check latest available version: %s' %
                       str(e)) from e
