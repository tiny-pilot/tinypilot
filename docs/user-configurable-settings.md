# User Configurable Settings

It is no longer possible to make changes to TinyPilot's undocumented settings through the `/home/tinypilot/settings.yml` file.

## Supported Settings

The following settings are supported and remain configurable through `settings.yml`:

- `janus_stun_port`
- `janus_stun_server`
- `tinypilot_external_port`
- `tinypilot_external_tls_port` (Pro only)
- `tinypilot_manage_tls_keys` (Pro only)
- `ustreamer_desired_fps`
- `ustreamer_edid`
- `ustreamer_h264_bitrate`
- `ustreamer_quality`

## Deprecated Settings (Legacy)

The following settings are configurable through `settings.yml`, but we may remove configuration support for them in the future:

- `tinypilot_keyboard_interface`
- `tinypilot_mouse_interface`
- `ustreamer_drop_same_frames`
- `ustreamer_encoder`
- `ustreamer_format`
- `ustreamer_resolution`
- `ustreamer_use_dv_timings`
- `ustreamer_workers`

## Unsupported Settings (Non-configurable)

The following settings are no longer configurable through `settings.yml`:

- `tinypilot_install_janus`
- `ustreamer_compile_janus_plugin`
- `ustreamer_h264_sink`
- `ustreamer_h264_sink_mode`
- `ustreamer_h264_sink_rm`
