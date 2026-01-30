import dataclasses
import json
import ssl
import urllib.request
from datetime import date

import flask

import env


class Error(Exception):
    pass


class VersionFileError(Error):
    pass


class CertificateNotYetValidError(Error):
    code = 'CERTIFICATE_NOT_YET_VALID'


class VersionRequestError(Error):
    pass


_VERSION_FILE = './VERSION'


@dataclasses.dataclass
class UpdateInfo:
    """Metadata about a TinyPilot update package.

    This data structure reflects the response of Gatekeeper’s
    `/available-update` routes.
    """
    version: str
    kind: str
    data: dict


def _is_debug():
    return flask.current_app.debug


def local_version():
    """Read the current local version string from the version file.

    If run locally, in development, where a version file is not present, then a
    dummy version string is returned.

    Returns:
        A version string (e.g., "1.2.3-16+7a6c812").

    Raises:
        VersionFileError: If an error occurred while accessing the version file.
    """
    if _is_debug():
        return '0.0.0-0+aaaaaaa'

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
    """Requests the latest release info from the TinyPilot Gatekeeper REST API.

    Returns:
        An UpdateInfo object, containing the information about the release.

    Raises:
        VersionRequestError: If an error occurred while making an HTTP request
            to the Gatekeeper API.
    """
    # The URL is trusted because it's not based on user input.
    url = f'{env.GATEKEEPER_BASE_URL}/community/available-update'
    try:
        # pylint: disable=line-too-long
        with urllib.request.urlopen(  # noqa: S310 # nosemgrep: dynamic-urllib-use-detected
                url,
                timeout=10) as response:
            response_bytes = response.read()
    except urllib.error.HTTPError as e:
        message = e.fp.read().decode('utf-8').strip()
        raise VersionRequestError(
            f'Failed to request latest available version: {message}') from e
    except urllib.error.URLError as e:
        if (isinstance(e.reason, ssl.SSLCertVerificationError) and
                e.reason.verify_message == 'certificate is not yet valid'):
            raise CertificateNotYetValidError(
                'Server\'s certificate start date is ahead of TinyPilot\'s'
                f' system date of {date.today():%Y-%m-%d}. Check the system'
                f' date to ensure that it is accurate. {e}') from e
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

    if not all(key in response_dict for key in ('version', 'kind', 'data')):
        raise VersionRequestError(
            'Failed to get latest available version because of an incompatible'
            ' response structure. Expected fields: version, kind, data. Got: '
            '' + ', '.join([*response_dict]) + '.')

    return UpdateInfo(version=response_dict['version'],
                      kind=response_dict['kind'],
                      data=response_dict['data'])
