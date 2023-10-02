import urllib.parse

import db.settings
from request_parsers import errors
from request_parsers import json


def parse_frame_rate(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (frame_rate,) = json.parse_json_body(request, required_fields=['frameRate'])
    try:
        frame_rate = _as_int(frame_rate)
        if not 1 <= frame_rate <= 30:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The frame rate must be a whole number between 1 and 30.') from e
    return frame_rate


def parse_mjpeg_quality(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (mjpeg_quality,) = json.parse_json_body(request,
                                            required_fields=['mjpegQuality'])
    try:
        mjpeg_quality = _as_int(mjpeg_quality)
        if not 1 <= mjpeg_quality <= 100:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingError(
            'The MJPEG quality must be a whole number between 1 and 100.'
        ) from e
    return mjpeg_quality


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


def parse_stun_address(request):
    """Parses a STUN address from a request.

    Args:
        request: Flask request object.

    Returns:
        A tuple containing (1) the hostname as string, and (2) the port as int.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (stun_address,) = json.parse_json_body(request,
                                           required_fields=['h264StunAddress'])
    # TODO make validation more robust and add more tests
    if stun_address is None:
        return None, None
    split_result = urllib.parse.urlsplit('//' + stun_address)
    return split_result.hostname, split_result.port


def _as_int(string):
    # Note: We need to cast the value to a string first otherwise the int
    # function forces floats into integers by simply cutting off the fractional
    # part. This may result in the value being incorrectly validated as an
    # integer.
    return int(str(string))
