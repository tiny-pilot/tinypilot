import logging
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


def local_head_commit_id():
    """Gets the commit ID from the HEAD of the local git repository.

    Returns:
        A str containing a git commit ID from the local HEAD.
        Example: 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05'

    Raises:
        Error: The git command failed.
    """
    logger.info('Getting local HEAD commit ID')
    return _run(['git', 'rev-parse', 'HEAD']).stdout.strip()


def remote_head_commit_id():
    """Gets the commit ID from the HEAD of the remote git repository.

    It needs to fetch git updates before retrieving the remote commit ID. It
    might cause a delay but it should be very minimal.

    Returns:
        A str containing a git commit ID from the origin/master HEAD.
        Example: 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05'

    Raises:
        Error: The git command failed.
    """
    logger.info('Getting remote HEAD commit ID')
    _fetch()
    return _run(['git', 'rev-parse', 'origin/master']).stdout.strip()


def _fetch():
    logger.info('Fetching changes')
    return _run(['git', 'fetch'])


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        raise Error(result.stderr.strip())
    return result
