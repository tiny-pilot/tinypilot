import subprocess

import update.settings

_UPDATE_SCRIPT_PATH = '/opt/tinypilot-privileged/update-video-settings'


class Error(Exception):
    pass


class VideoSettingsUpdateError(Error):
    pass


def get_fps():
    settings = update.settings.load_default()
    return settings.ustreamer_desired_fps


def set_fps(video_fps):
    settings = update.settings.load_default()
    settings.ustreamer_desired_fps = video_fps
    update.settings.save_default(settings)


def unset_fps():
    settings = update.settings.load_default()
    del settings.ustreamer_desired_fps
    update.settings.save_default(settings)


def apply():
    """Apply the current video settings found in the default settings file.

    Args:
        None
    Returns:
        stdout
    """
    try:
        return subprocess.check_output(['sudo', _UPDATE_SCRIPT_PATH],
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise VideoSettingsUpdateError(str(e.output).strip()) from e
