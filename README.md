# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/tiny-pilot/tinypilot)](https://github.com/tiny-pilot/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/tiny-pilot/tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

This branch has changes mainly in the `remote-screen.html` file where we connect to Janus to get the uStreamer stream in H264 format over WebRTC.

Currently all it does is connect to the Janus instance and fetch and display the stream.

## Technical Overview

There are five entities at play:

* uStreamer
* Janus uStreamer plugin
* Janus
* Janus JS client library
* TinyPilot frontend client

Janus serves as a WebRTC Gateway. To integrate with Janus for WebRTC communication, applications like uStreamer create custom Janus plugins to serve data over websockets and WebRTC. Janus provides the communication framework, and the plugin listens for and sends the messages from WebRTC clients.

uStreamer and the Janus uStreamer plugin communicate over shared memory. uStreamer writes the video stream to shared memory, and the uStreamer Janus plugin parses the video stream from the shared memory location.

The TinyPilot frontend client requests uStreamer's video stream by establishing a WebRTC connection to the uStreamer Janus plugin. The plugin serves the video stream from the shared memory it reads from uStreamer.

The communication flows like this: (TinyPilot frontend client) <-> (Janus) <-> (uStreamer)

### Technical Details

The details of the below described flow assumes the following setup:

* uStreamer is running
* uStreamer is providing an H264 stream over shared memory
* Janus is running with the uStreamer plugin loaded

When the user loads TinyPilot's web app, the frontend connects to the Janus websockets server using the [Janus JS client library](https://github.com/tiny-pilot/tinypilot/blob/3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c/app/static/js/janus.js).

Upon successful connection to Janus, TinyPilot attaches [to the uStreamer plugin](https://github.com/tiny-pilot/tinypilot/blob/3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c/app/templates/custom-elements/remote-screen.html#L94). Different plugins can provide different streams, so TinyPilot has to specify uStreamer explicitly.

If TinyPilot atttaches successfully to the uStreamer plugin, it gets a [handle object](https://github.com/tiny-pilot/tinypilot/blob/3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c/app/templates/custom-elements/remote-screen.html#L102), which allows TinyPilot to communicate directly to the uStreamer plugin.

The `attach` call also sets up a couple more callbacks like `success` for when the "attaching" succeeds, `onmessage` for handling messages sent by the plugin and `onremotestream` for when we receive a new video stream.

The uStreamer plugin apparently only handles [three message types](https://github.com/pikvm/ustreamer/blob/v4.11/janus/src/plugin.c#L475):  `watch`, `start` and `stop`.

As of 3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c, the `experimental/H264` branch only implements of the `watch` and `start` commands.

The `watch` command asks the plugin to initialize the WebRTC connection flow. TinyPilot sends the `watch` command in the success handler for the `attach` call. This command exchanges the offer and answer (called "jsep" for some reason by Janus, usually called SDP for session description protocol) and exchanges WebRTC candidates for connection.

After TinyPilot initializes the WebRTC connection, it expects to receive a message through the `onmessage` callback. TinyPilot checks if "jsep" is in the message to generate a WebRTC response.

If the WebRTC initialization fails, TinyPilot will receive an error message through the `onmessage` callback. The error message says [uStreamer hasn't found any SPS/PPS frames in the stream yet](https://github.com/pikvm/ustreamer/blob/v4.11/janus/src/plugin.c#L484). SPS/PPS frames are special H264 frames with meta information about the video (like the video dimensions for example). The only thing to do in this case is to retry sending the `watch` command. (refreshing the page also works, but is not a good solution for end-users)

It is important to note that up until now, even though we are connected via websockets we did not yet establish a WebRTC peer-to-peer connection.
TinyPilot and Janus are still exchanging messages over the Websockets channel.

When there is no error and there is actually a "jsep" present (the WebRTC offer) in the message, TinyPilot creates a WebRTC answer. The [`createAnswer` call](https://github.com/tiny-pilot/tinypilot/blob/3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c/app/templates/custom-elements/remote-screen.html#L114) creates the WebRTC answer and has a callback for when the WebRTC connection succeeds.

If the `createAnswer` call succeeds, TinyPilot sends a [`start` message](https://github.com/tiny-pilot/tinypilot/blob/3a3290c46c03280a31c9c3bae1bd267c3f4c7c2c/app/templates/custom-elements/remote-screen.html#L121), which triggers the plugin to begin streaming the video to the browser.

When the Janus uStreamer plugin begins the video stream, it triggers a call of the `onremotestream` callback. This handler receives the stream, which it can then attach to an existing `<video>` element.

Now the stream is connected and the remote screen's display should be visible in the browser.

The `stop` command tells the plugin code to "detach" from the shared memory provided by uStreamer. After receiving `stop` command, the Janus uStreamer plugin stops parsing H264 frames from uStreamer.

To restart a stream after TinyPilot has sent the `stop` command, TinyPilot must send the `watch` command again in order for the plugin to reattach to the shared memory. Only then can we send the `start`command again.

Note from Andre: I would probably recommend sending this command when the user leaves the page somehow for a cleaner shutdown/disconnect. However I haven't noticed any problem with just reloading the page which just breaks the websocket connection.

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
  mtlynch/ustreamer-janus:2022-02-02
```
