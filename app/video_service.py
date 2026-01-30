import contextlib
import logging
import subprocess

import db.settings

logger = logging.getLogger(__name__)

# To create a new EDID:
#  1. Convert the existing EDID to binary using "edid2bin".
#  2. Edit the binary using "AW EDID Editor v.02.00.13".
#  3. Save the new EDID in binary format.
#  4. Convert the binary EDID to a hex EDID using "make-edid".
#    - Use the "--yaml" option if required.
#
# Note: You may need to perform a few extra steps in order for the EDID
# to conform to edid-decode's check - but only if the "Display Range Limits"
# block changes. This is due to a bug in AW EDID Editor v.02.00.13 that doesn't
# set the correct bytes.
# To work around this:
#  1. Open the new EDID in "AW EDID Editor v.3.0.10".
#  2. Save the EDID to set correct bytes in the "Display Range Limits" block
#  3. Re-open the EDID in "AW EDID Editor v.02.00.13" and re-set
#     the screen size dimensions to 0 (both vertical and horizontal)
_EDID_PI4_FILE = '/usr/share/tinypilot/edid_pi4.hex'


def _get_default_edid():
    with contextlib.suppress(FileNotFoundError):
        with open(_EDID_PI4_FILE, encoding='utf-8') as file:
            return file.read().strip()

    return None


DEFAULT_EDID = _get_default_edid()
DEFAULT_MJPEG_FRAME_RATE = 30
DEFAULT_MJPEG_QUALITY = 80
DEFAULT_H264_BITRATE = 5000
DEFAULT_H264_STUN_SERVER = None
DEFAULT_H264_STUN_PORT = None


def restart():
    """Restarts the video streaming services for the remote screen.

    It only triggers the restart, but it doesn’t actually wait for it to
    complete.
    """
    _restart_ustreamer()
    use_webrtc = db.settings.Settings().get_streaming_mode(
    ) == db.settings.StreamingMode.H264
    if use_webrtc:
        _restart_janus()


def _restart_ustreamer():
    """Restarts uStreamer in a best-effort manner.

    In case the restart invocation failed, it ignores (but logs) the error.
    """
    logger.info('Triggering ustreamer restart...')
    try:
        subprocess.check_output(
            ['/usr/bin/sudo', '/usr/sbin/service', 'ustreamer', 'restart'],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to restart ustreamer: %s', e)
        return

    logger.info('Successfully restarted ustreamer')


def _restart_janus():
    """Restarts Janus in a best-effort manner.

    It also updates the Janus configuration (based on the settings file) before
    restarting.

    In case the restart invocation failed, it ignores (but logs) the error.
    """
    logger.info('Writing janus configuration...')
    try:
        subprocess.check_output([
            '/usr/bin/sudo', '/opt/tinypilot-privileged/scripts/configure-janus'
        ],
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to configure janus: %s', e)
        return

    logger.info('Triggering janus restart...')
    try:
        subprocess.check_output(
            ['/usr/bin/sudo', '/usr/sbin/service', 'janus', 'restart'],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError as e:
        logger.error('Failed to restart janus: %s', e)
        return

    logger.info('Successfully restarted janus')
