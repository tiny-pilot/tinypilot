import logging
import subprocess

_UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/scripts/update-video-settings'
DEFAULT_FPS = 30
DEFAULT_JPEG_QUALITY = 80
DEFAULT_H264_BITRATE = 5000
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
    logger.info('Running update-video-settings')
    try:
        output = subprocess.check_output(['sudo', _UPDATE_SCRIPT_PATH],
                                         stderr=subprocess.STDOUT,
                                         universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise VideoSettingsUpdateError(str(e.output).strip()) from e
    logger.info('update-video-settings completed successfully')
    return output
