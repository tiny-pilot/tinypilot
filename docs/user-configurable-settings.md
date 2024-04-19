# User Configurable Settings

It is no longer possible to make changes to TinyPilot's undocumented settings through the `/home/tinypilot/settings.yml` files. This document outlines which settings are supported, deprecated, and unsupported.

## Supported Settings

The following settings are supported and remain configurable through `settings.yml`:

- `janus_stun_port`
- `janus_stun_server`
- `tinypilot_external_port`
- `tinypilot_external_tls_port` (Pro only)
- `tinypilot_manage_tls_keys` (Pro only)
  - Whether TinyPilot manages TLS keys. Users can override this setting if they want to [provide their own TLS keys](https://tinypilotkvm.com/faq/own-tls-key).
- `ustreamer_desired_fps`
  - Desired frames per second. Defaults to 30 when not set.
- `ustreamer_edid`
  - EDID for TC358743 chip.
- `ustreamer_h264_bitrate`
  - Set the bitrate in Kb/s for the H264 stream (e.g., 2000). The range of allowed values is [25, 20000]. Defaults to 5000 when not set.
- `ustreamer_quality`
  - Quality of the JPEG encoding from 1 to 100 (best). Defaults to 80 when not set.

## Deprecated Settings (Legacy)

The following settings are still configurable through `settings.yml`, but we may remove configuration support for them in the future:

- `tinypilot_keyboard_interface`
- `tinypilot_mouse_interface`
- `ustreamer_drop_same_frames`
  - Number of same frames to drop.
- `ustreamer_encoder`
  - Encoding method to use, such as `m2m-image`.
- `ustreamer_format`
  - Device input format, such as `uyvy`.
- `ustreamer_resolution`
  - Stream resolution, such as `1280x720`.
- `ustreamer_use_dv_timings`
  - Whether to use Digital Video (DV) timings.
- `ustreamer_workers`
  - Number of worker threads to use.

## Unsupported Settings (Non-configurable)

The following settings are unsupported and no longer configurable through `settings.yml`:

- `tinypilot_debian_package_path`
- `tinypilot_enable_debug_logging`
- `tinypilot_install_janus`
- `tinypilot_interface`
- `tinypilot_port`
- `ustreamer_brightness`
- `ustreamer_capture_device`
- `ustreamer_compile_janus_plugin`
- `ustreamer_debian_package_path`
- `ustreamer_edids_dir`
- `ustreamer_h264_sink`
- `ustreamer_h264_sink_mode`
- `ustreamer_h264_sink_rm`
- `ustreamer_interface`
- `ustreamer_persistent`
- `ustreamer_port`
- `ustreamer_repo`
- `ustreamer_repo_version`
- `ustreamer_tcp_nodelay`
- `ustreamer_video_path`
