# Pi Virtual Keyboard

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

## Overview

Use your Raspberry Pi as a remote-controlled keyboard that accepts keystrokes through a web browser.

## Compatibility

* Raspberry Pi 4
* Raspberry Pi Zero W

## Installation

```bash
python3.7 -m venv venv
. venv/bin/activate
pip install --requirement requirements.txt
pip install --requirement dev_requirements.txt
hooks/enable_hooks
```

## Run

```bash
./serve
```
