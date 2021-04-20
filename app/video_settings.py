import logging
import subprocess

_UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/update-video-settings'
DEFAULT_FPS = 30
logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class VideoSettingsUpdateError(Error):
    pass


def apply():
    """Apply the current video settings found in the settings file.

    This runs the ustreamer ansible role using the systemd-config tag.

    Args:
        None

    Returns:
        A string consisting of the stdout and stderr output from the
        update-video-settings script.

    Raises:
        VideoSettingsUpdateError: If the script exits with a non-zero exit code.
    """
    try:
        logger.info('Running update-video-settings')
        output = subprocess.check_output(['sudo', _UPDATE_SCRIPT_PATH],
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
        logger.info('update-video-settings output: %s', output.strip())
    except subprocess.CalledProcessError as e:
        raise VideoSettingsUpdateError(str(e.output).strip()) from e
    return output
