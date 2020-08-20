# TinyPilot

[![CircleCI](https://circleci.com/gh/mtlynch/tinypilot.svg?style=svg)](https://circleci.com/gh/mtlynch/tinypilot) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Turn your Raspberry Pi into a browser-based KVM.

![TinyPilot demo](https://raw.githubusercontent.com/mtlynch/tinypilot/master/demo.gif)

## Pre-requisites

* Raspberry Pi OS Stretch or later
* python3-venv

## Hardware requirements

All-in-one kits are available from [tinypilotkvm.com](https://tinypilotkvm.com/order).

* [Raspberry Pi 4](https://amzn.to/3fdarLM) (all variants work)
* [HDMI to USB dongle](https://amzn.to/2YHEvJN)
  * It has no brand name, but you can identify them by sight.
  * They're available for $10-15 on eBay.
* [USB-C to USB-A](https://www.amazon.com/AmazonBasics-Type-C-USB-Male-Cable/dp/B01GGKYN0A/) cable (Male/Male)
* [microSD card](https://amzn.to/2VH0RcL) (Class 10, 8 GB or larger)
* [HDMI to HDMI cable](https://amzn.to/3gnlZwj)
  * Or \[other\] to HDMI, depending on how your target machine displays output.
* (Optional) [VGA to HDMI Adapter](https://amzn.to/30SZWYh)
  * If your target computer has VGA output, the above adapter is [confirmed to work](https://github.com/mtlynch/tinypilot/issues/76#issuecomment-664736402) with TinyPilot.

See ["TinyPilot: Build a KVM Over IP for Under $100"](https://mtlynch.io/tinypilot/#how-to-build-your-own-tinypilot) for a more detailed tutorial on how to assemble these parts to create a TinyPilot.

## Simple installation

The following installation steps:

* Create a service account for TinyPilot with limited priviliges.
* Install TinyPilot as a systemd service so it runs automatically on every boot.
* Install TinyPilot's dependencies.

From your Raspberry Pi device, run the following commands:

```bash
curl \
  --silent \
  --show-error \
  https://raw.githubusercontent.com/mtlynch/tinypilot/master/quick-install | \
    bash - && \
  sudo reboot
```

When your Pi reboots, you should be able to access TinyPilot by visiting your Pi hostname in the browser. For example, if your device is named `raspberrypi`:

* [http://raspberrypi/](http://raspberrypi/)

## Remote installation

If you have Ansible installed on your local machine, you can configure TinyPilot on a Raspberry Pi device using the [TinyPilot Ansible role](https://github.com/mtlynch/ansible-role-tinypilot). To configure TinyPilot remotely, run the following commands from your Ansible control node:

```bash
PI_HOSTNAME="raspberrypi" # Change to your pi's hostname
PI_SSH_USERNAME="pi"      # Change to your Pi username

# Install the TinyPilot Ansible role
ansible-galaxy install mtlynch.tinypilot

# Create a minimal Ansible playbook to configure your Pi
echo "- hosts: $PI_HOSTNAME
  roles:
    - role: mtlynch.tinypilot" > install.yml

ansible-playbook \
  --inventory "$PI_HOSTNAME", \
  --user "$PI_SSH_USERNAME" \
  --ask-pass \
  --become \
  --become-method sudo \
  install.yml

ansible \
  "$PI_HOSTNAME" \
  -m reboot \
  --inventory "$PI_HOSTNAME", \
  --user "$PI_SSH_USERNAME" \
  --ask-pass \
  --become \
  --become-method sudo
```

After running these commands, you should be able to access TinyPilot through a web browser at:

* [http://raspberrypi/](http://raspberrypi/)

## Developer installation

If you're interested in contributing to TinyPilot, follow these instructions to install the required developer packages in your development environment:

```bash
python3.7 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt

npm install prettier@2.0.5
```

To run TinyPilot's build scripts, run:

```bash
./dev-scripts/build
```

To enable TinyPilot's Git hooks, run:

```bash
./hooks/enable_hooks
```

To run TinyPilot on a non-Pi machine, run:

```bash
PORT=8000 KEYBOARD_PATH=/dev/null ./app/main.py
```

## Options

TinyPilot accepts various options through environment variables:

| Environment Variable | Default      | Description |
|----------------------|--------------|-------------|
| `HOST`               | `0.0.0.0`    | Network interface to listen for incoming connections. |
| `PORT`               | `8000`       | HTTP port to listen for incoming connections. |
| `KEYBOARD_PATH`      | `/dev/hidg0` | Path to keyboard HID interface. |

## Upgrades

The installation script is idempotent, so you can upgrade to the latest stable release of TinyPilot and its dependencies by just re-running [the quick install script](#simple-installation).

## Security considerations

TinyPilot does not support authentication. You should only use TinyPilot on networks that you trust. Anyone who accesses the TinyPilot URL can shutdown or restart your Pi and type arbitrary commands into the device to which your Pi is connected.

If you need authentication, the simplest solution would be to adjust your Nginx configuration (included by default with the installation) to require [HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/).

## Support

If this project is useful to you, consider making a financial contribution to support its development:

* [paypal.me/mtlynchio](https://paypal.me/mtlynchio)

## Detailed project updates

If you're interested in seeing what's happening with the project at a granular level, weekly updates appear every Friday on What Got Done:

* [What Got Done: TinyPilot](https://whatgotdone.com/michael/project/tinypilot)

## See also

* [TinyPilot Ansible Role](https://github.com/mtlynch/ansible-role-tinypilot): Use [Ansible](https://docs.ansible.com/ansible/latest/index.html) to install TinyPilot and all dependencies as a systemd service.

## Mailing list

For news about major TinyPilot releases and other updates about the project, sign up for the TinyPilot mailing list:

* [TinyPilot Mailing List](https://tinypilotkvm.com/about)
