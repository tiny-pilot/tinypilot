# Ansible Role: TinyPilot

## Role Variables

Available variables are listed below, along with default values (see [defaults/main.yml](defaults/main.yml)):

```yaml
tinypilot_interface: "127.0.0.1"
tinypilot_port: 58000
# The client is responsible for specifying the path/URL to the TinyPilot Debian
# package
tinypilot_debian_package_path: null
```

## Dependencies

- [tiny-pilot.ustreamer](../ansible-role-ustreamer)

## Example Playbook

## Building a TinyPilot Debian package

To install TinyPilot using the Ansible role, you need to provide the role with a path or URL to a TinyPilot Debian package.

To build a TinyPilot Debian package, run the following command:

```bash
../dev-scripts/build-debian-pkg
```

This will produce a TinyPilot Debian package under `./debian-pkg/releases`.

### `example.yml`

```yaml
- hosts: all
  roles:
    - role: ../ansible-role
      vars:
        tinypilot_debian_package_path: /path/to/tinypilot.deb
```

### Running Example Playbook

```bash
ansible-playbook example.yml
```

## Documentation

- [Introduction to the USB gadget driver](docs/usb-gadget-driver.md)
