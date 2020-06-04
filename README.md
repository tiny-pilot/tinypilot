# Key Mime Pi

[![CircleCI](https://circleci.com/gh/mtlynch/key-mime-pi.svg?style=svg)](https://circleci.com/gh/mtlynch/key-mime-pi) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a remote-controlled keyboard that accepts keystrokes through a web browser.

## Work in Progress

This is still a work in progress. I'll be improving the installation scripts and documentation in the next few weeks. ETA for a completed project is mid-June 2020.

## Compatibility

* Raspberry Pi 4
* Raspberry Pi Zero W

## Pre-requisites

* Raspbian OS 10 (Buster)
* USB Gadget Mode enabled on Raspberry Pi
  * Ansible users can configure everything through [ansible-role-key-mime-pi](https://github.com/mtlynch/ansible-role-key-mime-pi)
  * Instructions for non-Ansible users coming soon.

## Quick Start

```bash
sudo ./enable-usb-hid
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
PORT=8888 ./app/main.py
```

## Ansible installation

From your Ansible control node, run the following commands:

```bash
PI_HOSTNAME="raspberrypi" # Change to your pi's hostname

# Install the Key Mime Pi Ansible role
ansible-galaxy install mtlynch.keymimepi

# Create a minimal Ansible playbook to configure your Pi
echo "- hosts: $PI_HOSTNAME
  roles:
    - role: mtlynch.keymimepi" > install.yml

ansible-playbook --inventory "$PI_HOSTNAME", install.yml
```

## Development Installation

```bash
python3 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```