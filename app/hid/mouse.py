import logging

from hid import write as hid_write

logger = logging.getLogger(__name__)


def send_mouse_position(mouse_path, x, y, mouse_buttons):
    x_scaled, y_scaled = _scale_mouse_coordinates(x, y)
    logger.info('sending %d, %d to %s (button: %s)', x, y, mouse_path,
                mouse_buttons)

    buf = [0] * 5
    buf[0] = mouse_buttons
    buf[1] = x_scaled & 0xff
    buf[2] = (x_scaled >> 8) & 0xff
    buf[3] = y_scaled & 0xff
    buf[4] = (y_scaled >> 8) & 0xff

    logger.info("buf=%s", buf)
    hid_write.write_to_hid_interface(mouse_path, buf)


def _scale_mouse_coordinates(x, y):
    x_scaled = x * 32767.0
    y_scaled = y * 32767.0
    return int(x_scaled), int(y_scaled)
