# TinyPilot's Architecture

## Overview

![TinyPilot Architecture](https://docs.google.com/drawings/d/e/2PACX-1vR48PdVelUodnzk7az1FE4pNX4WK3l3YRas8Ty8fnE-2qE-DN5AYXsHD26F4OJgmGSZkmGGJgs0RvpT/pub?w=903&amp;h=792)

## TinyPilot frontend

The TinyPilot frontend runs in the user's browser. It is responsible for:

* Presenting the target computer's video stream in the browser window
* Forwarding keyboard and mouse input to the [TinyPilot backend](#tinypilot-backend)
* Offering friendly interfaces for the user to change TinyPilot's settings

The TinyPilot frontend is a pure HTML/CSS/JS app. It has no build or compilation step and no framework like Vue, Angular, or React. It uses external libraries as little as possible.

The frontend makes heavy use of [HTML Custom Elements](https://css-tricks.com/creating-a-custom-element-from-scratch/). Modern browsers support these natively. TinyPilot's custom elements try to mirror the style of Vue's [Single File Components](https://vuejs.org/v2/guide/single-file-components.html).

TinyPilot's custom elements can be found in [app/templates/custom-elements](./app/templates/custom-elements).

## TinyPilot backend

The backend is a Flask application. It offers handles three types of requests:

* Page requests
  * To serve a page like the main `/` view, TinyPilot uses Flask to pre-render a template.
* REST requests
  * When the frontend makes a request to the backend to query server state or perform some action (e.g., `/api/shutdown`), the backend handles it through REST handlers.
* WebSockets requests
  * To handle requests for keystrokes or mouse movements, the backend needs something faster than regular HTTP REST requests, so it uses a WebSockets channel.

The backend is responsible for sending keyboard and mouse input to the target computer via its USB gadgets (see [USB gadgets](#usb-gadgets) section, below).

## USB gadgets

TinyPilot impersonates keyboard and mouse input using the Linux [USB Gadget API](https://www.kernel.org/doc/html/v4.13/driver-api/usb/gadget.html).

To use the USB Gadget API, a device needs a USB port that operates in either device mode or supports USB OTG (which allows the port to switch between host mode and device mode). The Raspberry Pi 4B's USB-C port is the only port on the device capable of USB OTG, so this is the port that TinyPilot uses.

TinyPilot [presents itself](https://github.com/tiny-pilot/ansible-role-tinypilot/blob/594be69c86fcdeaa9488690b2aef951acaf3bf64/files/init-usb-gadget) to the target computer as a USB Multifunction Composite Gadget (i.e., a USB hub) with a USB keyboard and mouse attached. This allows TinyPilot to send both keyboard and mouse input through a single USB connection.

## nginx

[nginx](https://nginx.org/) is a popular open-source web server and reverse proxy.

TinyPilot uses nginx to listen to incoming HTTP requests and proxy them to the correct internal component. It also serves all of TinyPilot's static resources (i.e., files that don't need to go through Flask for server-side processing).

## uStreamer

[uStreamer](https://github.com/pikvm/ustreamer) is a third-party video streaming tool. It is much faster than other options and generally delivers a stream on a local network with latency between 100-200ms.

Its workflow is:

1. Capture video from an HDMI capture device
1. Encode the video to MJPEG (if it's not already MJPEG) and apply any other video transformations
1. Stream the video over an HTTP endpoint

Modern browsers support MJPEG natively, but it has a few drawbacks:

1. It's bandwidth-hungry, as a 30 frames-per-second stream means sending 30 JPEG images per second
1. Browser implementation tends to be buggy since it's not a common format

As of Feb. 2021, uStreamer's maintainer is working on a H264 option, expected to be available in Q1 or Q2 2021. This will likely alleviate issues around MJPEG.

## Installation

TinyPilot's installation process is somewhat unusual in that it depends on Ansible. The [`get-tinypilot.sh`](./get-tinypilot.sh) script bootstraps an Ansible environment on a Raspberry Pi and then uses [`ansible-role-tinypilot`](https://github.com/tiny-pilot/ansible-role-tinypilot) to install itself locally. `ansible-role-tinypilot` transitively includes other roles that TinyPilot depends on such as [`ansible-role-ustreamer`](https://github.com/mtlynch/ansible-role-ustreamer) and [`ansible-role-nginx`](https://github.com/geerlingguy/ansible-role-nginx).

The `get-tinypilot.sh` script is also responsible for version-to-version updates and configuration changes.
