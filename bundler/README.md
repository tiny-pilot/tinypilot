# Bundler

The bundler is responsible for creating a single-file distributable, with which TinyPilot can be installed on the target device.

A few notes for context:

- This repository (`tinypilot`) contains the source code of the TinyPilot web service. While the web service is the main component of the TinyPilot software, a complete installation has other TinyPilot-specific dependencies, which reside in separate repositories.
- The bundler code (i.e. everything inside [`/bundler`](/bundler)) could theoretically live in a separate repository, but we decided to put it here to keep our repository structure simple.

## Components

### Bundle

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

The entrypoint for installing the bundle is the [`bundle/install`](bundle/install) script. It does some bootstrapping and then hands over to `ansible-role-tinypilot`, which contains most of the actual installation logic.

### Gatekeeper Web Service

Gatekeeper is our web service where the bundles are hosted and distributed. [See here](https://github.com/tiny-pilot/gatekeeper) for more info.

New bundles are automatically uploaded via our build platform:

- For Community, every commit to the `master` branch is released
- For Pro, only tags with particular format (e.g. `2.4.1`) are released

### `get-tinypilot.sh`

The installation process is facilitated by the [`get-tinypilot.sh`](../get-tinypilot.sh) (`get-tinypilot-pro.sh` for Pro) script.

For installing TinyPilot on the target device, the `get-tinypilot.sh` script unpacks the bundle and invokes the [`install`](bundle/install) script.

On a fresh device, the user runs the script manually. On a device with an existing TinyPilot installation, the script is invoked “under the hood” throughout the update process.

The `get-tinypilot.sh` script is idempotent, so it’s safe to run repeatedly.

## Installation Process

The installation procedure consists of the following steps. The procedure is slightly different between TinyPilot Community and Pro.

### TinyPilot Community

1. `get-tinypilot.sh` script retrieves latest bundle from Gatekeeper
1. `get-tinypilot.sh` script unpacks bundle to `/opt/tinypilot-updater` and invokes `install` script

### TinyPilot Pro

1. `get-tinypilot-pro.sh` checks whether a version flag was specified.
   - If no version flag was supplied, `get-tinypilot-pro.sh` asks Gatekeeper what the latest available version is.
1. `get-tinypilot-pro.sh` requests the bundle with the desired version from Gatekeeper.
1. `get-tinypilot-pro.sh` script unpacks bundle to `/opt/tinypilot-updater` and invokes `install` script

## Update Process

When performing a version-to-version update, the above installation procedure is carried out automatically after the user had triggered an update from the UI:

1. From the TinyPilot web UI, the user clicks “System” > “Update”
1. The backend returns two versions:
   - The one that is currently installed on the system.
   - The latest available version, which is returned from Gatekeeper.
1. If the versions are different, the frontend shows an “Update” button.
1. When the user clicks on “Update”, the backend runs the [update launcher](../app/update/launcher.py) asynchronously.
1. The update launcher starts the `tinypilot-updater` systemd service.
1. The `tinypilot-updater` systemd service executes the [`update-service`](../scripts/update-service) Python script.
1. The `update-service` invokes the privileged `/opt/tinypilot-privileged/update` script.
1. The privileged `update` service downloads and hands over to `get-tinypilot.sh`/`get-tinypilot-pro.sh` (see above).

This indirection in the update flow is necessary since the TinyPilot web service runs with limited privileges for security reasons. Therefore, the actual update process has to be carried out via a systemd service, which has root privileges.

There is one main difference between the Community and Pro edition:

- On TinyPilot Community, the update process always installs the latest available version (i.e., built from the latest commit to the `master` branch).
- On TinyPilot Pro, the update process installs the particular version that was returned from Gatekeeper and shown in the UI.

## History

Until August 2022, the installation and update flows used to look differently. The rationale behind the overhaul are described in detail in the [“update overhaul document”](https://github.com/tiny-pilot/tinypilot-pro/blob/experimental/update-overhaul/UPDATE-WORKFLOW.md). The implementation of the overhaul was facilitated via [this mega ticket](https://github.com/tiny-pilot/tinypilot-pro/issues/445).

On a high level, the differences were:

- The previous update flow relied on git repositories. So instead of shipping a self-contained bundle, new code was deployed via `git pull`. While this worked well, we felt that the entire setup was quite complex.
- There were no license checks for TinyPilot Pro. Instead, the Pro source code was protected only via the “secret” URL of the git mirror.
- Because the legacy update flow depended on commodity Git hosting, it prevented us from controlling important parts of the update experience such as ensuring valid version transitions, phasing rollouts into stages, and performing license checks.
