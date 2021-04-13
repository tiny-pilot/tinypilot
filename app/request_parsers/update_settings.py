from request_parsers import errors
from request_parsers import message as message_parser
from request_parsers.validators import \
    update_settings as update_settings_validator


def parse_video_fps(request):
    message = message_parser.parse_message(request, ['video_fps'])
    video_fps = message['video_fps']
    if not update_settings_validator.validate_video_fps(video_fps):
        raise errors.InvalidVideoFpsError(
            'The video FPS must be an whole number between 1 and 30.')
    return int(str(video_fps))
