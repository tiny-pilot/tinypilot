# Bundler

The bundler is responsible for creating a single-file distributable called “TinyPilot bundle”.

Note that this repository (`tinypilot`) contains the source code of the TinyPilot web service. While the web service is the main component of the TinyPilot software, a complete installation has other TinyPilot-specific dependencies, which reside in separate repositories.

## Components

### Bundle

The TinyPilot bundle contains all the TinyPilot-owned code required to install TinyPilot on a device.

The [`create-bundle`](create-bundle) script generates the bundle from the [`bundle/`](bundle) folder. That folder contains a few “static” configuration files. At build time, the `create-bundle` script adds the following dependencies:

- **The TinyPilot web service**
  - The root [`Dockerfile`](../Dockerfile) packs the TinyPilot web service as a Debian package from the source files.
- **Several Ansible roles**
  - The main role is [`ansible-role-tinypilot`](../ansible-role), which then fetches the roles for [nginx](https://github.com/tiny-pilot/ansible-role-nginx) and [ustreamer](https://github.com/tiny-pilot/ansible-role-ustreamer).
  - The Ansible roles are responsible for configuring TinyPilot and its dependencies on the device.
- **Metadata**
  - E.g., version/build information

The entrypoint for installing the bundle is the [`bundle/install`](bundle/install) script. It does some bootstrapping and then hands over to [`ansible-role-tinypilot`](../ansible-role), which contains most of the actual installation logic.

### Gatekeeper Web Service

Gatekeeper is TinyPilot’s web service for hosting and distributing bundles. See [the Gatekeeper README](https://github.com/tiny-pilot/gatekeeper) for more info.

Our CircleCI pipeline automatically builds and uploads new bundles to Gatekeeper:

- For Community, it releases every commit to the `master` branch
- For Pro, it only releases tags with a particular format (e.g., `2.4.1`)

### `get-tinypilot.sh`

[`get-tinypilot.sh`](../get-tinypilot.sh) (`get-tinypilot-pro.sh` for Pro) facilitates the installation process.

For installing TinyPilot on the device, `get-tinypilot.sh` unpacks the bundle to `/mnt/tinypilot-installer` and invokes the [`install`](bundle/install) script.

To avoid excessive writes to the filesystem, the bundle is downloaded and unpacked on a volatile RAMdisk mounted at `/mnt/tinypilot-installer`.

On a fresh device, the user runs `get-tinypilot.sh` manually. On a device with an existing TinyPilot installation, TinyPilot’s update process invokes `get-tinypilot.sh` “under the hood”.

`get-tinypilot.sh` is idempotent, so it’s safe to run repeatedly.

## Installation Process

The installation procedure consists of the following steps. The procedure is slightly different between TinyPilot Community and Pro.

### TinyPilot Community

1. `get-tinypilot.sh` retrieves latest bundle from Gatekeeper.
2. `get-tinypilot.sh` unpacks bundle to `/mnt/tinypilot-installer` and invokes `install` script.

### TinyPilot Pro

1. `get-tinypilot-pro.sh` checks whether the caller supplied a version flag.
   - If the version flag is absent, `get-tinypilot-pro.sh` asks Gatekeeper what the latest available version is.
1. `get-tinypilot-pro.sh` requests the bundle with the desired version from Gatekeeper.
1. `get-tinypilot-pro.sh` script unpacks bundle to `/opt/tinypilot-updater` and invokes `install` script.

## Update Process

When performing a version-to-version update, TinyPilot carries out the above installation procedure automatically after the user requests an update via the web UI.

1. From the TinyPilot web UI, the user clicks “System” > “Update”.
1. TinyPilot’s web service backend returns two versions:
   - The one that is currently installed on the device.
   - The latest available version, which the TinyPilot web service retrieves from Gatekeeper.
1. If the versions are different, the frontend shows an “Update” button.
1. When the user clicks on “Update”, TinyPilot’s web service backend runs the [update launcher](../app/update/launcher.py) asynchronously.
   - On TinyPilot Pro, the update launcher stores the desired target version in a file.
1. The update launcher starts the `tinypilot-updater` systemd service.
1. The `tinypilot-updater` systemd service executes the [`update-service`](../scripts/update-service) Python script.
1. The `update-service` invokes the privileged `/opt/tinypilot-privileged/scripts/update` script.
1. The privileged `update` script downloads `get-tinypilot.sh`/`get-tinypilot-pro.sh` (see above) and executes that script in the privileged context.
   - On TinyPilot Pro, the privileged `update` script reads and passes on the target version from the file that the update launcher had populated previously.

The indirection in the update flow has the following reasons:

- The system update is a long-running process, so we use systemd to run it asynchronously.
- To avoid an elevation of privilege vulnerability, the `update-service` (owned by the `tinypilot` user) delegates to the privileged `update` script (owned by the `root` user).

There is one main difference between the Community and Pro edition:

- On TinyPilot Community, the update process always installs the latest available version (i.e., built from the latest commit to the `master` branch).
- On TinyPilot Pro, the update process installs the particular version that was returned from Gatekeeper and shown in the UI.

## History

Until August/September 2022, the installation and update flows used to look differently. You can read up on the rationale behind the overhaul in detail in the [“update overhaul document”](https://github.com/tiny-pilot/tinypilot-pro/blob/experimental/update-overhaul/UPDATE-WORKFLOW.md). We broke down the overhaul into individual tasks, which you can find in [this mega ticket](https://github.com/tiny-pilot/tinypilot-pro/issues/445).

From a high level, the differences were:

- The previous update flow relied on git repositories. So instead of shipping a self-contained bundle, the deployment of new code happened via `git pull`. However, `git` is not the right tool for software distribution, so over time we ran into several issues and limitations with this setup.
- There were no license checks for TinyPilot Pro. Instead, the only protection mechanism of the Pro source code was by keeping the URL of the git mirror secret.
- Because the legacy update flow depended on commodity Git hosting, it prevented us from controlling important parts of the update experience such as ensuring valid version transitions, phasing rollouts into stages, and performing license checks.
