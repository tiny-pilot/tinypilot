# Key Mime Pi

[![CircleCI](https://circleci.com/gh/mtlynch/key-mime-pi.svg?style=svg)](https://circleci.com/gh/mtlynch/key-mime-pi) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a remote-controlled keyboard that accepts keystrokes through a web browser.

## Compatibility

* Raspberry Pi 4
* Raspberry Pi Zero W

## Pre-requisites

* Raspbian OS 10 (Buster)
* git
* pip
* python3-venv

## Quick Start

To begin, enable USB gadget support on the Pi by running the following commands:

```bash
sudo ./enable-usb-hid
sudo reboot
```

When the Pi reboots, run Key Mime Pi with the following commands:

```
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
PORT=8000 ./app/main.py
```

Key Mime Pi will be running in your browser at:

* [http://raspberrypi:8000/](http://raspberrypi:8000/)

## Ansible installation

From your Ansible control node, run the following commands:

```bash
PI_HOSTNAME="raspberrypi" # Change to your pi's hostname
PI_SSH_USERNAME="pi"      # Change to your Pi username

# Install the Key Mime Pi Ansible role
ansible-galaxy install mtlynch.keymimepi

# Create a minimal Ansible playbook to configure your Pi
echo "- hosts: $PI_HOSTNAME
  roles:
    - role: mtlynch.keymimepi" > install.yml

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

You should be able to access Key Mime Pi through a web browser at:

* [http://raspberrypi:8000/](http://raspberrypi:8000/)

## Development Installation

If you're interesting in contributing to Key Mime Pi, follow these instructions to install the required developer packages in your development environment:

```bash
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

To run Key Mime Pi's build scripts, run:

```bash
./build
```

To enable Key Mime Pi's Git hooks, run:

```bash
./hooks/enable_hooks
```

## Options

Key Mime Pi accepts various options through environment variables:

| Environment Variable | Default      | Description |
|----------------------|--------------|-------------|
| `HOST`               | `0.0.0.0`    | Network interface to listen for incoming connections. |
| `PORT`               | `8000`       | HTTP port to listen for incoming connections. |
| `HID_PATH`           | `/dev/hidg0` | Path to keyboard HID interface. |