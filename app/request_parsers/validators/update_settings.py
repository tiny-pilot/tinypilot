# Source: https://en.wikipedia.org/wiki/Display_resolution#Common_display_resolutions
_COMMON_DISPLAY_RESOLUTIONS = {
    '800x600',
    '1024x768',
    '1280x720',
    '1280x800',
    '1280x1024',
    '1360x768',
    '1366x768',
    '1440x900',
    '1536x864',
    '1600x900',
    '1680x1050',
    '1920x1080',
}


def validate_video_resolution(value):
    return str(value) in _COMMON_DISPLAY_RESOLUTIONS


def validate_video_fps(value):
    try:
        assert 1 <= int(str(value)) <= 30
    except (ValueError, AssertionError):
        return False
    else:
        return True


def validate_video_jpeg_quality(value):
    try:
        assert 1 <= int(str(value)) <= 100
    except (ValueError, AssertionError):
        return False
    else:
        return True
