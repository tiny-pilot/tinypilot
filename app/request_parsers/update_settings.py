from request_parsers import errors
from request_parsers import message as message_parser
from request_parsers.validators import update_settings as update_settings_validator


def parse_settings(request):
    return message_parser.parse_message(request, [])


def parse_video_resolution(request):
    message = message_parser.parse_message(request, ['video_resolution'])
    video_resolution = message['video_resolution']
    if not update_settings_validator.validate_video_resolution(video_resolution):
        raise errors.InvalidVideoResolutionError(
            'The video resolution must be a common display resolution as'
            ' listed here: https://en.wikipedia.org/wiki/Display_resolution#Common_display_resolutions')
    return str(video_resolution)


def parse_video_fps(request):
    message = message_parser.parse_message(request, ['video_fps'])
    video_fps = message['video_fps']
    if not update_settings_validator.validate_video_fps(video_fps):
        raise errors.InvalidVideoFpsError(
            'The video FPS must be an whole number between 1 and 30.')
    return int(str(video_fps))


def parse_video_jpeg_quality(request):
    message = message_parser.parse_message(request, ['video_jpeg_quality'])
    video_jpeg_quality = message['video_jpeg_quality']
    if not update_settings_validator.validate_video_jpeg_quality(video_jpeg_quality):
        raise errors.InvalidVideoJpegQualityError(
            'The video JPEG quality must be a whole number between 1 and 100.')
    return int(str(video_jpeg_quality))
