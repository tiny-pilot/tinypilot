# KVM Pi

[![CircleCI](https://circleci.com/gh/mtlynch/kvmpi.svg?style=svg)](https://circleci.com/gh/mtlynch/kvmpi) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a browser-based KVM.

[![KVM Pi screenshot](https://raw.githubusercontent.com/mtlynch/kvmpi/master/screenshot.png)](https://raw.githubusercontent.com/mtlynch/kvmpi/master/screenshot.png)

## Compatibility

* Raspberry Pi 4
* Raspberry Pi Zero W

## Pre-requisites

* Raspberry Pi OS Stretch or later
* git
* pip
* python3-venv

## Hardware requirements

TODO

## Quick Start

To begin, enable USB gadget support on the Pi by running the following commands:

```bash
sudo ./enable-usb-hid
sudo reboot
```

When the Pi reboots, run KVM Pi with the following commands:

```
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
PORT=8000 ./app/main.py
```

KVM Pi will be running in your browser at:

* [http://raspberrypi:8000/](http://raspberrypi:8000/)

## Ansible installation

The Ansible installation is a more thorough install, as it does the following:

* Creates a service account for KVM Pi with limited priviliges.
* Installs KVM Pi as a systemd service so it runs automatically on every boot.
* Installs KVM Pi's dependencies.

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

## See also

* [KVM Pi Ansible Role](https://github.com/mtlynch/ansible-role-kvmpi): Use [Ansible](https://docs.ansible.com/ansible/latest/index.html) to install KVM Pi and all dependencies as a systemd service.