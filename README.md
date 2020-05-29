# Pi Virtual Keyboard

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a remote-controlled keyboard that accepts keystrokes through a web browser.

## Compatibility

* Raspberry Pi 4
* Raspberry Pi Zero W

## Pre-requisites

* Python 3.7+
* python3-venv

## Quick Start

```bash
python3.7 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
PORT=8888 ./app/main.py
```

## Development Installation

```bash
python3.7 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```