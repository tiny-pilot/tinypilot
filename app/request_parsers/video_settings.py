import ipaddress
import re

import db.settings
from request_parsers import errors
from request_parsers import json

_DOMAIN_PATTERN = re.compile(r'^[0-9a-z-.]{1,255}$')


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


def parse_h264_stun_address(request):
    """Parses the STUN address (server + port) from a request.

    The server can be a valid domain name, or an IP address (IPv4 / IPv6). The
    server and port values must either both be present, or both absent.

    Args:
        request: A Flask request object.

    Returns:
        A tuple containing (1) the server as string, and (2) the port as int.

    Raises:
        InvalidVideoSettingStunAddress
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (
        server,
        port,
    ) = json.parse_json_body(request,
                             required_fields=['h264StunServer', 'h264StunPort'])
    server = _parse_h264_stun_server(server)
    port = _parse_h264_stun_port(port)
    if (server is None and port is not None) or (server is not None and
                                                 port is None):
        raise errors.InvalidVideoSettingStunAddressError(
            'The server and port values must either both be given, or both '
            'absent.')
    return server, port


def _parse_h264_stun_server(server):
    if server is None:
        return None
    if not isinstance(server, str):
        raise errors.InvalidVideoSettingStunAddressError(
            'The server value must be of type string.')
    try:
        ipaddress.ip_address(server)
        return server
    except ValueError:
        pass
    if not _DOMAIN_PATTERN.match(server):
        raise errors.InvalidVideoSettingStunAddressError(
            'The server must be a valid domain name or IP address (IPv4/IPv6).')
    return server


def _parse_h264_stun_port(port):
    if port is None:
        return None
    try:
        port = _as_int(port)
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError as e:
        raise errors.InvalidVideoSettingStunAddressError(
            'The port must be a positive integer, not greater than 65535.') \
            from e
    return port


def _as_int(string):
    # Note: We need to cast the value to a string first otherwise the int
    # function forces floats into integers by simply cutting off the fractional
    # part. This may result in the value being incorrectly validated as an
    # integer.
    return int(str(string))
