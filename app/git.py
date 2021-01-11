import logging
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


def local_head_commit_id():
    """Gets local HEAD commit ID.

    Executes, via _run(), a command to get the local HEAD commit ID.

    Returns:
        A str containing a git commit ID from the local HEAD.
        Example: 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05'

    Raises:
        An Error object with the stderr produced by subprocess.run()
    """
    logger.info('Getting local HEAD commit ID')
    return _run(['git', 'rev-parse', 'HEAD']).stdout.strip()


def remote_head_commit_id():
    """Gets origin/master HEAD commit ID.

    Fetches the repository with the private _fetch() function and then
    executes, via _run(), a command to get the origin/master HEAD commit ID.

    Returns:
        A str containing a git commit ID from the origin/master HEAD.
        Example: 'bf07bfe72941457cf068ca0a44c6b0d62dd9ef05'

    Raises:
        An Error object with the stderr produced by subprocess.run(). It can be
        raised by both the _fetch() call and the direct _run() call containing
        the command to get the commit ID.
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
