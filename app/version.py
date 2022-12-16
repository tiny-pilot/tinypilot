import json
import urllib.request

import flask


class Error(Exception):
    pass


class VersionFileError(Error):
    pass


class VersionRequestError(Error):
    pass


_VERSION_FILE = './VERSION'


def _is_debug():
    return flask.current_app.debug


def local_version():
    """Read the current local version string from the version file.

    If run locally, in development, where a version file is not present, then a
    dummy version string is returned.

    Returns:
        A version string (e.g., "1.2.3-16").

    Raises:
        VersionFileError: If an error occurred while accessing the version file.
    """
    if _is_debug():
        return '0.0.0-0'

    try:
        with open(_VERSION_FILE, encoding='utf-8') as file:
            version = file.read().strip()
    except UnicodeDecodeError as e:
        raise VersionFileError(
            'The local version file must only contain UTF-8 characters.') from e
    except IOError as e:
        raise VersionFileError(f'Failed to check local version: {e}') from e
    if version == '':
        raise VersionFileError('The local version file cannot be empty.')
    return version


def latest_version():
    """Requests the latest version from the TinyPilot Gatekeeper REST API.

    Returns:
        A version string (e.g., "1.2.3-16").

    Raises:
        VersionRequestError: If an error occurred while making an HTTP request
            to the Gatekeeper API.
    """
    try:
        with urllib.request.urlopen(
                'https://gk.tinypilotkvm.com/community/available-update',
                timeout=10) as response:
            response_bytes = response.read()
    except urllib.error.URLError as e:
        raise VersionRequestError(
            f'Failed to request latest available version: {e}') from e

    try:
        response_text = response_bytes.decode('utf-8')
    except UnicodeDecodeError as e:
        raise VersionRequestError(
            'Failed to decode latest available version response body as UTF-8'
            ' characters.') from e

    try:
        response_dict = json.loads(response_text)
    except json.decoder.JSONDecodeError as e:
        raise VersionRequestError(
            'Failed to decode latest available version response body as JSON.'
        ) from e

    if not isinstance(response_dict, dict):
        raise VersionRequestError(
            'Failed to decode latest available version response body as a JSON'
            ' dictionary.')

    if 'version' not in response_dict:
        raise VersionRequestError(
            'Failed to get latest available version because of a missing field:'
            ' version')

    return response_dict['version']
