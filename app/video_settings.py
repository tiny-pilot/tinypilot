import logging
import subprocess

DEFAULT_FRAME_RATE = 30
DEFAULT_MJPEG_QUALITY = 80
DEFAULT_H264_BITRATE = 5000
logger = logging.getLogger(__name__)


class Error(Exception):
    pass


class VideoSettingsUpdateError(Error):
    pass


def apply():
    """Apply the current video settings found in the settings file.

    Args:
        None

    Returns:
        None

    Raises:
        VideoSettingsUpdateError: If the script exits with a non-zero exit code.
    """
    for service in ('ustreamer', 'janus'):
        logger.info('Restarting %s to apply new video settings', service)
        try:
            subprocess.check_output(
                ['sudo', '/usr/sbin/service', service, 'restart'],
                stderr=subprocess.STDOUT,
                universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise VideoSettingsUpdateError(str(e.output).strip()) from e

    logger.info(
        'Finished restarting video services to apply new video settings')
