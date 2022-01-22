# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/tiny-pilot/tinypilot)](https://github.com/tiny-pilot/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/tiny-pilot/tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

This branch has changes mainly in the `remote-screen.html` file where we connect to Janus to get the uStreamer stream in h264 format over webrtc.

Currently all it does is connect to the Janus instance and fetch and display the stream.

### Notes

To fetch the stream one must "talk" to the uStreamer plugin. Apparently it only receives 3 messages: `watch`, `start` and `stop`.
This can be checked here: https://github.com/pikvm/ustreamer/blob/master/janus/src/plugin.c#L475
This commit only shows usage of the `watch` and `start` commands.

The `watch` command is used to ask the plugin to perform the initial WebRTC connection flow.
This is essentially exchanging the offer and answer (called jsep for some reason  by Janus, usually called SDP for session description protocol) and exchanging webrtc candidates for connection.

The plugin also sends messages back when its status changes. Usually you'd just get `started` and `stopped` after sending `start`and `stop` commands respectively.

But there is also an error that is worth catching and reacting to. This error can come after the `watch` command and happens when the plugin hasn't seen any SPS/PPS frames.
These are special h264 frames with meta information abbout the video (like the video dimensions for example). You can see the error is pushed by the plugin here: https://github.com/pikvm/ustreamer/blob/master/janus/src/plugin.c#L484

Currently the code doesn't react to it but I guess the way to go would be attempting to send the `watch` command shortly after.
Usually the SPS/PPS frames are sent along with the keyframes and usually these are configured to be sent once every second.

## Pre-requisites

* Raspberry Pi OS Stretch or later
* python3-venv

## Install

### Docker

```bash
curl -fsSL https://get.docker.com | sudo sh && \
  sudo usermod -aG docker $(whoami)
```

### TinyPilot

```bash
  curl \
  --silent \
  --show-error \
  https://raw.githubusercontent.com/tiny-pilot/tinypilot/experimental/h264/quick-install | \
    bash - && \
  sudo reboot
```

## Run

You need to start Janus and uStreamer manually every time the device reboots:

```bash
docker run \
  --privileged \
  --network host \
  --name janus-ustreamer \
  mtlynch/ustreamer-janus:2022-01-17
```
