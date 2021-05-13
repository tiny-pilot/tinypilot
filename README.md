# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/mtlynch/tinypilot)](https://github.com/mtlynch/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/mtlynch/tinypilot.svg?style=svg)](https://circleci.com/gh/mtlynch/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

Turn your Raspberry Pi into a browser-based KVM.

[![TinyPilot demo](https://raw.githubusercontent.com/mtlynch/tinypilot/master/readme-assets/demo-800w.gif)](https://raw.githubusercontent.com/mtlynch/tinypilot/master/readme-assets/demo.gif)

<https://tinypilotkvm.com>

## Features

* Video capture (HDMI/DVI/VGA)
* Keyboard forwarding
* Mouse forwarding
* Fullscreen mode
* Paste text from clipboard

## Official builds

TinyPilot official hardware packages give you everything you need to run TinyPilot and allows you to fund TinyPilot's development for future improvements.

### [TinyPilot Voyager](https://tinypilotkvm.com/product/tinypilot-voyager)

[![Photo of TinyPilot Voyager](https://raw.githubusercontent.com/mtlynch/tinypilot/master/readme-assets/voyager-side-cables.jpg)](https://tinypilotkvm.com/product/tinypilot-voyager)

Voyager is TinyPilot's professional-grade KVM over IP device. Its quiet, compact design makes it a great fit for professional environments such as offices, data centers, and server rooms.

### [TinyPilot Hobbyist Kit](https://tinypilotkvm.com/product/tinypilot-hobbyist-kit)

[![Photo of TinyPilot Voyager](https://raw.githubusercontent.com/mtlynch/tinypilot/master/readme-assets/hobbyist-kit.jpg)](https://tinypilotkvm.com/product/tinypilot-hobbyist-kit)

The TinyPilot Hobbyist Kit is a great fit for home users who want a low-cost, DIY KVM over IP device.

## Build your own

All-in-one kits are available from [tinypilotkvm.com](https://tinypilotkvm.com/order).

* [Raspberry Pi 4](https://smile.amazon.com/dp/B07TD42S27) (all variants work)
* [HDMI to USB dongle](https://smile.amazon.com/dp/B08CXWPYQ8/)
  * [In smaller form factor](https://smile.amazon.com/dp/B08C9FCF2X/)
  * They have no brand name, and there are several variants, but they're all built on the same MacroSilicon 2109 chip.
  * They're available for $10-15 on eBay and AliExpress.
* [3 Amp power supply](https://smile.amazon.com/dp/B0728HB18G)
* [USB-C to USB-A](https://smile.amazon.com/dp/B01GGKYN0A/) cable (Male/Male)
* [microSD card](https://smile.amazon.com/dp/B073K14CVB/) (Class 10, 8 GB or larger)
* [HDMI to HDMI cable](https://smile.amazon.com/dp/B014I8SSD0/)
  * Or \[other\] to HDMI, depending on how your target machine displays output.
* (Optional) [A USB-C OTG split connector](https://tinypilotkvm.com/product/tinypilot-power-connector): Supports continuous power when the target computer turns off.
  * Requires two additional [USB-A to microUSB cables](https://smile.amazon.com/dp/B01JPDTZXK/) and a [3 Amp power adapter](https://smile.amazon.com/dp/B0728HB18G).
  * If you're using this split connector, choose a USB-C to USB-A cable that's [12" or shorter](https://smile.amazon.com/dp/B012V56D2A/) to minimize voltage drop along the cable.
* (Optional) [VGA to HDMI Adapter](https://smile.amazon.com/dp/B07121Y1Z3/)
  * If your target computer has VGA output, the above adapter is [confirmed to work](https://github.com/mtlynch/tinypilot/issues/76#issuecomment-664736402) with TinyPilot.

See ["TinyPilot: Build a KVM Over IP for Under $100"](https://mtlynch.io/tinypilot/#how-to-build-your-own-tinypilot) for a more detailed tutorial on how to assemble these parts to create a TinyPilot.

## Pre-requisites

* Raspberry Pi OS Stretch or later
* python3-venv

## Simple installation

You can install TinyPilot on a compatible Raspberry Pi in just two commands.

```bash
curl \
  --silent \
  --show-error \
  https://raw.githubusercontent.com/mtlynch/tinypilot/master/quick-install | \
    bash - && \
  sudo reboot
```

The installation process:

* Creates a service account for TinyPilot with limited priviliges.
* Installs TinyPilot as a systemd service so it runs automatically on every boot.
* Installs TinyPilot's dependencies.
* Installs TinyPilot to the `/opt/tinypilot` directory.

When your Pi reboots, you should be able to access TinyPilot by visiting your Pi hostname in the browser. For example, if your device is named `raspberrypi`:

* [http://raspberrypi/](http://raspberrypi/)

## Developer installation

See the [CONTRIBUTING](CONTRIBUTING.md) file.

## Other installation options

* [Advanced installation options](https://github.com/mtlynch/tinypilot/wiki/Installation-Options#advanced-installation)
* [Remote installation via Ansible](https://github.com/mtlynch/tinypilot/wiki/Installation-Options#remote-installation)

## Updates

To update to the latest version of TinyPilot, run the update script:

```bash
/opt/tinypilot/scripts/upgrade && sudo reboot
```

## Diagnostics

If you're having trouble with TinyPilot, you can retrive logs from the web dashboard by clicking "Logs" in the bottom of the main dashboard.

If you can't access the web dashboard, you can retrieve the logs by SSHing into the device and running the following command:

```bash
/opt/tinypilot/dev-scripts/dump-logs
```

This log is useful if you [file a bug report](https://github.com/mtlynch/tinypilot/issues/new?assignees=&labels=&template=bug_report.md&title=).

You can read more details about the logs [in the wiki](https://github.com/mtlynch/tinypilot/wiki/Troubleshooting-and-Diagnostics).

## Security considerations

TinyPilot does not support authentication or transport-level encryption. You should only use TinyPilot on networks that you trust. Anyone who accesses the TinyPilot URL can shutdown or restart your Pi and type arbitrary commands into the device to which your Pi is connected.

To use TinyPilot on untrusted networks, you can upgrade to [TinyPilot Pro](https://tinypilotkvm.com/product/tinypilot-pro), which adds password-based authentication and TLS for end-to-end encryption.

As a free alternative, you can adjust your Nginx configuration (included by default with the installation) to require [HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/) and add a self-signed TLS certificate.

## Support

If this project is useful to you, consider making a financial contribution to support its development:

* [paypal.me/tinypilotkvm](https://paypal.me/tinypilotkvm)

## Detailed project updates

If you're interested in seeing what's happening with the project at a granular level, weekly updates appear every Friday on What Got Done:

* [What Got Done: TinyPilot](https://whatgotdone.com/michael/project/tinypilot)

## See also

* [TinyPilot Wiki](https://github.com/mtlynch/tinypilot/wiki): Guides for tasks related to TinyPilot.
* [TinyPilot Ansible Role](https://github.com/mtlynch/ansible-role-tinypilot): Use [Ansible](https://docs.ansible.com/ansible/latest/index.html) to install TinyPilot and all dependencies as a systemd service.

## Acknowledgments

TinyPilot would not be possible without the excellent and generous work from many open source projects, the most notable of which are listed below:

* [uStreamer](https://github.com/pikvm/ustreamer)
* [Flask](https://github.com/pallets/flask) and [Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
* [vdesktop](https://github.com/Botspot/vdesktop)
* [litestream](https://litestream.io)
* [Raspberry Pi](https://www.raspberrypi.org/)
* [nginx](https://nginx.org/) and [ansible-role-nginx](https://github.com/geerlingguy/ansible-role-nginx)

## Mailing list

For news about major TinyPilot releases and other updates about the project, sign up for the TinyPilot mailing list:

* [TinyPilot Mailing List](https://tinypilotkvm.com/about)

## Upgrade to Pro

TinyPilot Pro includes additional features for professional users, including:

* [Virtual drive mounting and booting](https://tinypilotkvm.com/blog/whats-new-in-1-5#boot-into-a-virtual-disk-drive)
* Password-based authentication

Support the project and upgrade to Pro at <https://tinypilotkvm.com/product/tinypilot-pro>.
