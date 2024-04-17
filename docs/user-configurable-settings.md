# User Configurable Settings

It is no longer possible to make changes to TinyPilot's undocumented settings through the `/home/tinypilot/settings.yml` file.

## Supported Settings

The following settings are supported and remain configurable through `settings.yml`:

- `tinypilot_external_port`
- `tinypilot_external_tls_port` (Pro only)
- `tinypilot_manage_tls_keys` (Pro only)
- `ustreamer_edid`
- `ustreamer_desired_fps`
- `ustreamer_quality`
- `ustreamer_h264_bitrate`
- `janus_stun_server`
- `janus_stun_port`

## Unsupported Settings (Legacy)

The following settings are configurable through `settings.yml`, but we may remove configuration support for them in the future:

- `tinypilot_keyboard_interface`
- `tinypilot_mouse_interface`
- `ustreamer_*`
  - Any uStreamer specific settings that are not explicitly supported above.
