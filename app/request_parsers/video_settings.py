import db.settings
from request_parsers import errors
from request_parsers import json


def parse_fps(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (fps,) = json.parse_json_body(request, required_fields=['fps'])
    try:
        fps = _as_int(fps)
        if not 1 <= fps <= 30:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The video FPS must be a whole number between 1 and 30.') from e
    return fps


def parse_jpeg_quality(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (jpeg_quality,) = json.parse_json_body(request,
                                           required_fields=['jpegQuality'])
    try:
        jpeg_quality = _as_int(jpeg_quality)
        if not 1 <= jpeg_quality <= 100:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The video JPEG quality must be a whole number between 1 and 100.'
        ) from e
    return jpeg_quality


def parse_h264_bitrate(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (h264_bitrate,) = json.parse_json_body(request,
                                           required_fields=['h264Bitrate'])
    try:
        h264_bitrate = _as_int(h264_bitrate)
        if not 25 <= h264_bitrate <= 20000:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The H264 bitrate must be a whole number between 25 and 20000.'
        ) from e
    return h264_bitrate


def parse_streaming_mode(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (streaming_mode,) = json.parse_json_body(request,
                                             required_fields=['streamingMode'])
    try:
        return db.settings.StreamingMode(streaming_mode)
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The video streaming mode must be `MJPEG` or `H264`.') from e


def _as_int(string):
    # Note: We need to cast the value to a string first otherwise the int
    # function forces floats into integers by simply cutting off the fractional
    # part. This may result in the value being incorrectly validated as an
    # integer.
    return int(str(string))
