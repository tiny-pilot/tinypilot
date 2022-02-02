# TinyPilot

[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/tiny-pilot/tinypilot)](https://github.com/tiny-pilot/tinypilot/graphs/contributors)
[![CircleCI](https://circleci.com/gh/tiny-pilot/tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/tinypilot)
[![Reddit](https://img.shields.io/badge/reddit-join-orange?logo=reddit)](https://www.reddit.com/r/tinypilot)
[![Twitter](https://img.shields.io/twitter/follow/tinypilotkvm?label=Twitter&style=social)](https://twitter.com/tinypilotkvm)

## Overview

This branch has changes mainly in the `remote-screen.html` file where we connect to Janus to get the uStreamer stream in h264 format over webrtc.

Currently all it does is connect to the Janus instance and fetch and display the stream.

## Technical Overview

There are 3 entities at play here. The tinypilot frontend client, Janus and uStreamer.

It is important to remember that Janus only serves as a WebRTC Gateway.
This means plugins have to be developed for it in order to have some actual functionality.
The plugins can then make use of features that Janus provides to control the flow of communication while the connection flow and the media exchange are abstracted away.

In this case we are loading Janus with a plugin for uStreamer.
The uStreamer plugin primarily makes use of the websocket functionality of Janus.
This is used to easily exchange messages with the frontend client.
The websocket communication in the frontend client is abstracted away by client provided in the Janus repository.
With this in mind we can consider that talking to "Janus" or the "uStreamer plugin" to be the same thing.
The only differentiation to be had is that Janus provides all the communication framework but it is the plugin that listens for and sends the messages.

When the frontend client communicates with the uStreamer plugin it will be able to request the video stream.
This is when the uStreamer plugin actually communicates with uStreamer, however only indirectly.
The uStreamer application, when started, provides the stream over shared memory. The uStreamer plugin attaches to that shared memory and parses the frames from there.

The communication always flows like this: (frontend client) <-> (Janus) <-> (uStreamer)


### Technical Details

The details of the below described flow are considering that Janus is up and running with the uStreamer
plugin loaded and also that uStreamer itself is running and providing the h264 stream over shared memory.

When the tinypilot page is loaded the Janus client is loaded as well and tries to connect to the Jaus websocket server.

Upon success we must explicitly attach to a plugin (since different plugins can provide different streams and api altogether).

Upon success of attaching to the uStreamer plugin we get a handle object with which we can communicate with the uStreamer plugin specifically.
The `attach` call also sets up a couple more callbacks like `success` for when the "attaching" succeeds,
`onmessage` for handling messages sent by the plugin and `onremotestream` for when we receive a new video stream.
The uStreamer plugin apparently only handles 3 different messages:  `watch`, `start` and `stop`.
This can be checked here: https://github.com/pikvm/ustreamer/blob/v4.11/janus/src/plugin.c#L475
Messages are strictly exchanged between the frontend code and the plugin code while Janus itself only provides the communication framework.
This commit only shows usage of the `watch` and `start` commands.

The `watch` command is used to ask the plugin to perform the initial WebRTC connection flow. It is sent in the success handler for the `attach` call.
This is essentially exchanging the offer and answer (called jsep for some reason by Janus, usually called SDP for session description protocol) and exchanging webrtc candidates for connection.

After that it is expected that we get a message that will be handled by the `onmessage` callback.
Here we check if there is this "jsep" in the message to generate a webrtc response.
It is important to note that up until now, even though we are connected via websockets we did not yet establish a webrtc peer-to-peer connection.
The messages are still sent over the websocket channel while the webrtc connection is used for media (e.g. video).
It might also happen that we actually receive an error message (still over this `onmessage` channel), I believe it comes from here: https://github.com/pikvm/ustreamer/blob/v4.11/janus/src/plugin.c#L484
It says it hasn't found any SPS/PPS frames in the stream yet. These are special h264 frames with meta information about the video (like the video dimensions for example).
I believe here one can simply retry sending the `watch` command. (Personally I've only tried refreshing the page and that usually is enough).

When there is no error and there is actually a "jsep" present (the webrtc offer) in the message we can create a webrtc answer.
The `createAnswer` call used for creating the webrtc answer also has a callback for when the webrtc connection succeeds.
It is here where we send the `start` message. This will trigger the plugin to start sending the video stream.

When the video stream is created from the plugin side it will trigger a call of the `onremotestream` handler defined earlier.
This handler gets the stream which it can then attach to an existing `<video>` element.

Now the stream is connected and we should be seeing the remote screen.

Finally, usage of the `stop` command. This command tells the plugin code to "detach" from the shared memory provided by uStreamer.
This means that the plugin won't be parsing anymore h264 frames from the uStreamer.
To restart we must send the `watch` command again in order for the plugin to reattach to the shared memory.
Only then can we send the `start`command again.
I would probably recommend sending this command when the user leaves the page somehow for a cleaner shutdown/disconnect.
However I haven't noticed any problem with just reloading the page which just breaks the websocket connection.

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
