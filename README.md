# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/tiny-pilot/tinypilot)](https://github.com/tiny-pilot/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/tiny-pilot/tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

Turn your Raspberry Pi into a browser-based KVM.

[![TinyPilot demo](https://raw.githubusercontent.com/tiny-pilot/tinypilot/master/readme-assets/demo-800w.gif)](https://raw.githubusercontent.com/tiny-pilot/tinypilot/master/readme-assets/demo.gif)

<https://tinypilotkvm.com>

## Features

- Video capture (HDMI/DVI/VGA)
- Keyboard forwarding
- Mouse forwarding
- Fullscreen mode
- Paste text from clipboard

## Official builds

TinyPilot official hardware packages give you everything you need to run TinyPilot and allows you to fund TinyPilot's development for future improvements.

### [TinyPilot Voyager 2a](https://tinypilotkvm.com/product/tinypilot-voyager2a)

[![Photo of TinyPilot Voyager 2a](https://raw.githubusercontent.com/tiny-pilot/tinypilot/master/readme-assets/voyager2a-600px.webp)](https://tinypilotkvm.com/product/tinypilot-voyager2a)

Voyager 2a is TinyPilot's professional-grade KVM over IP device. Its quiet, compact design makes it a great fit for professional environments such as offices, data centers, and server rooms.

## Build your own

- [Raspberry Pi 4](https://smile.amazon.com/dp/B07TD42S27) (all variants work)
- [HDMI to USB dongle](https://smile.amazon.com/dp/B08CXWPYQ8/)
  - They have no brand name, and there are several variants, but they're all built on the same MacroSilicon 2109 chip.
  - They're available for \$10-15 on eBay and AliExpress.
- [3 Amp power supply](https://smile.amazon.com/dp/B0728HB18G)
- [USB-C to USB-A](https://smile.amazon.com/dp/B01GGKYN0A/) cable (Male/Male)
- [microSD card](https://smile.amazon.com/dp/B073K14CVB/) (Class 10, 8 GB or larger)
- [HDMI to HDMI cable](https://smile.amazon.com/dp/B014I8SSD0/)
  - Or \[other\] to HDMI, depending on how your target machine displays output.
- (Optional) [A USB-C OTG split connector](https://tinypilotkvm.com/product/tinypilot-power-connector): Supports continuous power when the target computer turns off.
  - Requires two additional [USB-A to microUSB cables](https://smile.amazon.com/dp/B01JPDTZXK/) and a [3 Amp power adapter](https://smile.amazon.com/dp/B0728HB18G).
  - If you're using this split connector, choose a USB-C to USB-A cable that's [12" or shorter](https://smile.amazon.com/dp/B012V56D2A/) to minimize voltage drop along the cable.
- (Optional) [VGA to HDMI Adapter](https://smile.amazon.com/dp/B07121Y1Z3/) - If your target system has VGA output.
  - Alternatively, you can replace the VGA to HDMI adapter and HDMI to USB dongle with a [VGA to USB adapter](https://smile.amazon.com/dp/B08GYXZC3D).

See ["TinyPilot: Build a KVM Over IP for Under \$100"](https://mtlynch.io/tinypilot/#how-to-build-your-own-tinypilot) for a more detailed tutorial on how to assemble these parts to create a TinyPilot.

## Pre-requisites

- Raspberry Pi OS Bullseye (32-bit)
- python3-venv

## Simple installation

You can install TinyPilot on a compatible Raspberry Pi in just two commands.

```bash
curl \
  --silent \
  --show-error \
  https://raw.githubusercontent.com/tiny-pilot/tinypilot/master/get-tinypilot.sh | \
    bash - && \
  sudo reboot
```

When your Pi reboots, you should be able to access TinyPilot by visiting your Pi hostname in the browser. For example, if your device is named `raspberrypi`:

- [http://raspberrypi/](http://raspberrypi/)

If you're using an [HDMI to CSI capture chip](https://github.com/tiny-pilot/tinypilot/wiki/HDMI-Capture-Devices#toshiba-tc358743-capture-devices) (such as with a TinyPilot Voyager series device), see [the additional configuration steps](https://github.com/tiny-pilot/tinypilot/wiki/Installation-Options#example-tc358743-hdmi-to-csi-capture-chip) required for video capture.

## Developer installation

See the [CONTRIBUTING](CONTRIBUTING.md) file.

## Other installation options

- [Advanced installation options](https://github.com/tiny-pilot/tinypilot/wiki/Installation-Options#advanced-installation)

## Diagnostics

If you're having trouble with TinyPilot, you can retrive logs from the web dashboard by clicking "Logs" in the bottom of the main dashboard.

If you can't access the web dashboard, you can retrieve the logs by SSHing into the device and running the following command:

```bash
sudo /opt/tinypilot-privileged/scripts/collect-debug-logs
```

This log is useful if you [file a bug report](https://github.com/tiny-pilot/tinypilot/issues/new?assignees=&labels=&template=bug_report.md&title=).

You can read more details about the logs [in the wiki](https://github.com/tiny-pilot/tinypilot/wiki/Troubleshooting-and-Diagnostics).

## Security considerations

TinyPilot does not support authentication or transport-level encryption. You should only use TinyPilot on networks that you trust. Anyone who accesses the TinyPilot URL can shutdown or restart your Pi and type arbitrary commands into the device to which your Pi is connected.

To use TinyPilot on untrusted networks, you can upgrade to [TinyPilot Pro](https://tinypilotkvm.com/product/tinypilot-pro), which adds password-based authentication and TLS for end-to-end encryption.

As a free alternative, you can adjust your Nginx configuration (included by default with the installation) to require [HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) and add a self-signed TLS certificate.

## Detailed project updates

If you're interested in seeing what's happening with the project at a granular level, weekly updates appear every Friday on What Got Done:

- [What Got Done: TinyPilot](https://whatgotdone.com/michael/project/tinypilot)

## See also

- [TinyPilot Wiki](https://github.com/tiny-pilot/tinypilot/wiki): Guides for tasks related to TinyPilot.

## Acknowledgments

TinyPilot would not be possible without the excellent and generous work from many open source projects, the most notable of which are listed below:

- [uStreamer](https://github.com/pikvm/ustreamer)
- [Flask](https://github.com/pallets/flask) and [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
- [vdesktop](https://github.com/Botspot/vdesktop)
- [litestream](https://litestream.io)
- [Raspberry Pi](https://www.raspberrypi.org/)
- [nginx](https://nginx.org/)

## Mailing list

For news about major TinyPilot releases and other updates about the project, sign up for the TinyPilot mailing list:

- [TinyPilot Mailing List](https://tinypilotkvm.com/about)

## Upgrade to Pro

TinyPilot Pro includes additional features for professional users, including:

- [Virtual drive mounting and booting](https://tinypilotkvm.com/blog/whats-new-in-1-5#boot-into-a-virtual-disk-drive)
- Password-based authentication

Support the project and upgrade to Pro at <https://tinypilotkvm.com/product/tinypilot-pro>.
