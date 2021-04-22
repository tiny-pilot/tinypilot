from request_parsers import errors
from request_parsers import message as message_parser
from request_parsers.validators import video_fps as video_fps_validator


def parse(request):
    message = message_parser.parse_message(request,
                                           required_fields=['videoFps'])
    try:
        # Note: We need to cast the value to a string first otherwise the int
        # function forces floats into integers by simply cutting off the
        # fractional part. This results in the value being incorrectly
        # validated as an integer.
        video_fps = int(str(message['videoFps']))
        if not video_fps_validator.validate(video_fps):
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoFpsError(
            'The video FPS must be an whole number between 1 and 30.') from e
    return video_fps
