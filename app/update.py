import logging
import subprocess

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class VersionError(Error):
    pass


class UpdateError(Error):
    pass


def version():
    logger.info('Getting version')
    cmd = ['git', 'describe', '--always']
    return _exec_version(cmd)


def latest_release():
    logger.info('Getting latest release')
    cmd = [
        'git', 'ls-remote', 'https://github.com/mtlynch/tinypilot.git',
        'refs/heads/master'
    ]
    return _exec_version(cmd)


def update():
    logger.info('Updating version')
    cmd = ['sudo', '/opt/tinypilot-privileged/update']
    return _exec_update(cmd)


def _exec_version(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if 'failed' in result.stderr.lower():
        raise VersionError(result.stdout + result.stderr)
    else:
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.info(result.stderr)
    return result.stdout.split('refs')[0].strip()[0:7]


def _exec_update(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if 'failed' in result.stderr.lower():
        raise UpdateError(result.stdout + result.stderr)
    else:
        if result.stdout:
            logger.info(result.stdout)
        if result.stderr:
            logger.info(result.stderr)
    return True
