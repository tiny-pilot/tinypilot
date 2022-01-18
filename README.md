# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/tiny-pilot/tinypilot)](https://github.com/tiny-pilot/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/tiny-pilot/tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

## Pre-requisites

* Raspberry Pi OS Stretch or later
* python3-venv

## Install TinyPilot

```bash
sudo sed -i '/^tinypilot_repo_branch/d' /home/tinypilot/settings.yml && \
  curl \
  --silent \
  --show-error \
  https://raw.githubusercontent.com/tiny-pilot/tinypilot/experimental/h264/quick-install | \
    bash - && \
  sudo reboot
```

## Install uStreamer and Janus

Install Docker and log out for permissions to take effect:

```bash
curl -fsSL https://get.docker.com | sudo sh && \
  sudo usermod -aG docker $(whoami) &&
  logout
```

Then run Janus and uStreamer under Docker:

```bash
docker run \
  --privileged \
  --network host \
  --name janus-ustreamer \
  mtlynch/ustreamer-janus:2022-01-17
```
