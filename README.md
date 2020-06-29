# KVM Pi

[![CircleCI](https://circleci.com/gh/mtlynch/kvmpi.svg?style=svg)](https://circleci.com/gh/mtlynch/kvmpi) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a browser-based KVM.

![KVM Pi demo](https://raw.githubusercontent.com/mtlynch/kvmpi/master/demo.gif)

## Pre-requisites

* Raspberry Pi OS Stretch or later
* python3-venv

## Hardware requirements

* Raspberry Pi 4
* TODO: List remaining hardware

## Installation

The following installation steps:

* Create a service account for KVM Pi with limited priviliges.
* Install KVM Pi as a systemd service so it runs automatically on every boot.
* Install KVM Pi's dependencies.

From your Raspberry Pi device, run the following commands:

```bash
curl -sSL https://raw.githubusercontent.com/mtlynch/kvmpi/master/quick-install | bash -
sudo reboot
```

When your Pi reboots, you should be able to access KVM Pi by visiting your Pi hostname in the browser. For example, if your device is named `raspberrypi`:

* [http://raspberrypi/](http://raspberrypi/)

## Remote installation

If you'd prefer to run Ansible from a remote machine, you 

To install the [KVM Pi Ansible role](https://github.com/mtlynch/ansible-role-kvmpi), run the following commands from your Ansible control node:

```bash
PI_HOSTNAME="raspberrypi" # Change to your pi's hostname
PI_SSH_USERNAME="pi"      # Change to your Pi username

# Install the KVM Pi Ansible role
ansible-galaxy install mtlynch.kvmpi

# Create a minimal Ansible playbook to configure your Pi
echo "- hosts: $PI_HOSTNAME
  roles:
    - role: mtlynch.kvmpi" > install.yml

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

You should be able to access KVM Pi through a web browser at:

* [http://raspberrypi/](http://raspberrypi/)

## Development Installation

If you're interesting in contributing to KVM Pi, follow these instructions to install the required developer packages in your development environment:

```bash
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

To run KVM Pi's build scripts, run:

```bash
./build
```

To enable KVM Pi's Git hooks, run:

```bash
./hooks/enable_hooks
```

To run KVM Pi on a non-Pi machine, run:

```bash
PORT=8000 HID_PATH=/dev/null ./app/main.py
```

## Options

KVM Pi accepts various options through environment variables:

| Environment Variable | Default      | Description |
|----------------------|--------------|-------------|
| `HOST`               | `0.0.0.0`    | Network interface to listen for incoming connections. |
| `PORT`               | `8000`       | HTTP port to listen for incoming connections. |
| `HID_PATH`           | `/dev/hidg0` | Path to keyboard HID interface. |

## Security considerations

KVM Pi does not support authentication. You should only use KVM Pi on networks that you trust. Anyone who accesses the KVM Pi URL can shutdown or restart your Pi and type arbitrary commands into the device to which your Pi is connected.

If you need authentication, the easiest option is to place KVM Pi behind an Nginx instance and require [HTTP Basic Authentication](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/).

## Support

If this project is useful to you, consider making a financial contribution to support its development:

* [paypal.me/mtlynchio](https://paypal.me/mtlynchio)

## See also

* [KVM Pi Ansible Role](https://github.com/mtlynch/ansible-role-kvmpi): Use [Ansible](https://docs.ansible.com/ansible/latest/index.html) to install KVM Pi and all dependencies as a systemd service.