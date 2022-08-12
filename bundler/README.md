# Bundler

The bundler is responsible for creating a single-file distributable, with which TinyPilot can be installed on the target device.

A few structural notes for context:

- This repository only contains the source code of the TinyPilot web service. While the web service is the main component of the TinyPilot software, a complete installation has other TinyPilot-specific dependencies, which reside in separate repositories.
- The bundler code (i.e. everything inside [`/bundler`](/bundler)) could theoretically live in a separate repository, but we decided to put it here to keep our repository structure simple.

## Components

### Bundle Structure

The TinyPilot bundle is built from the [`bundle/`](bundle) folder by running the [`create-bundle`](create-bundle) script.

Everything that’s inside the [`bundle/`](bundle) folder will be shipped to the device. At build time, the `create-bundle` script adds the following dependencies to the bundle:

- **The TinyPilot web service**
  - It’s built from the root [`Dockerfile`](../Dockerfile) and embedded as Debian package
  - On the device, the Debian package is installed to `/opt/tinypilot`
- **Several Ansible roles**
  - The main role is [`ansible-role-tinypilot`](https://github.com/tiny-pilot/ansible-role-tinypilot), which then fetches the roles for [nginx](https://github.com/tiny-pilot/ansible-role-nginx) and [ustreamer](https://github.com/tiny-pilot/ansible-role-ustreamer).
  - The responsibility of the Ansible roles is to configure the target system
- **Meta-data**
  - For example, version/build information

On the target system, the bundle is unpacked to `/opt/tinypilot-updater`. It’s necessary to persist the bundle folder on the device, because the application still relies on the Ansible roles being there for applying system changes. We might refactor this in the future, though.

### `get-tinypilot.sh` script

[`get-tinypilot.sh`](../get-tinypilot.sh) is the entrypoint for performing a full install or update on the target device.

- On a fresh device, the user runs the script manually.
- On a device with an existing TinyPilot installation, the script is invoked “under the hood” throughout the update process.
- When creating disk images with Packer, the script is invoked with a special, pre-configured license.

### Gatekeeper Web Service

Gatekeeper is our web service where the bundles are hosted and distributed. [See here](https://github.com/tiny-pilot/gatekeeper) for more info.

New bundles are automatically uploaded via our build platform:

- For Community, every commit to the `master` branch is released
- For Pro, only tags with particular format (e.g. `2.4.1`) are released

## Installation / Update Process

For installing TinyPilot on the target device, the `get-tinypilot.sh` script unpacks the bundle and invokes the [`install`](bundle/install) script.

The installation procedure consists of the following steps. Note that the procedure is slightly different between TinyPilot Community and Pro.

> TODO: Add Pro-specific info, once we have fully implemented it.

1. `get-tinypilot.sh` script retrieves latest bundle from Gatekeeper
1. `get-tinypilot.sh` script unpacks bundle to `/opt/tinypilot-updater` and invokes `install` script
1. `install` script pulls dependencies (e.g. system packages and Python libraries)
1. `install` script invokes Ansible role

When performing an update, the above procedure is carried out automatically after the user had triggered an update:

1. From the TinyPilot web UI, the user clicks "System" > "Update"
1. TinyPilot runs the `tinypilot-updater` systemd service
1. `tinypilot-updater` service runs [`update-service`](../scripts/update-service) Python script
1. `update-service` invokes privileged `/opt/tinypilot-privileged/update` script
1. Privileged `update` service hands over to `get-tinypilot.sh` (see above)

This indirection in the update flow is necessary since the TinyPilot web service runs with limited privileges for security reasons. Therefore, the actual update process has to be carried out via a systemd service, which has root privileges.

## History

Until August 2022, the installation and update flows used to look differently. The rationale behind the overhaul are described in detail in the [“update overhaul document”](https://github.com/tiny-pilot/tinypilot-pro/blob/experimental/update-overhaul/UPDATE-WORKFLOW.md). The implementation of the overhaul was facilitated via [this mega ticket](https://github.com/tiny-pilot/tinypilot-pro/issues/445).

On a high level, the differences were:

- The previous update flow relied on git repositories. So instead of shipping a self-contained bundle, new code was basically deployed via `git pull`. While this basically worked well, we felt that the entire setup was still quite complex.
- There were no license checks for TinyPilot Pro. Instead, the Pro source code was protected only via the “secret” URL of the git mirror.
- Since the legacy update flow wasn’t hosted on our own infrastructure, we didn’t have much insight into usage or telemetrics.
