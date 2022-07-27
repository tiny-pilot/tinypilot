# Bundler

The bundler is responsible for creating a single-file distributable, with which TinyPilot can be installed on the target device.

## Components

### Bundle Structure

The TinyPilot bundle is built from the [`bundle/`](bundle) folder by running the [`create-bundle`](create-bundle) script. At build time, it adds the following dependencies to the bundle:

- The TinyPilot web service:
  - Built from [`Dockerfile`](../Dockerfile) as Debian package
  - On the device: installed to `/opt/tinypilot`
- Several Ansible roles:
  - Their responsibility is to configure the target system
  - See e.g. [`ansible-role-tinypilot`](https://github.com/tiny-pilot/ansible-role-tinypilot)
- Meta-data, e.g. Version information

On the target system, the bundle is unpacked to the `/opt/tinypilot-updater` folder. This is necessary, so that the application can re-run the Ansible roles for applying config changes.

### `get-tinypilot.sh` script

[`get-tinypilot.sh`](../get-tinypilot.sh) is the “entrypoint” for performing a full install or update on the target device.

- On a fresh device, the user runs the script manually.
- On a device with an existing TinyPilot installation, the script is invoked “under the hood” throughout the update process.
- When creating disk images with Packer, the script is invoked with a special, pre-configured license.

### Gatekeeper Web Service

Gatekeeper is our web service where the bundles are hosted and distributed. [See here](https://github.com/tiny-pilot/gatekeeper) for more info.

New bundles get automatically uploaded via our build platform:

- For Community, every commit to the `master` branch is released
- For Pro, only release tags (e.g. `2.4.1`) are released

## Installation / Update Process

For installing TinyPilot on the target device, the `get-tinypilot.sh` script unpacks the bundle and invokes the [`install`](bundle/install) script.

The `install` script performs the following steps. Note, that the procedure is slightly different between TinyPilot Community and Pro.

1. **PRO** `get-tinypilot.sh` checks license.
2. **PRO|COMMUNITY** `get-tinypilot.sh` script retrieves bundle from Gatekeeper.
3. **PRO|COMMUNITY** `get-tinypilot.sh` script unpacks bundle to `/opt/tinypilot-updater` and invokes `install` script.
4. ... (etc.; basically, take over the description from the overhaul document)

## History

### Legacy Update Flow

(Briefly summarize the “old” update system; also reference the overhaul project)
