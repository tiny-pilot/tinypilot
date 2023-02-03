# Ansible Role: TinyPilot

[![CircleCI](https://circleci.com/gh/tiny-pilot/ansible-role-tinypilot.svg?style=svg)](https://circleci.com/gh/tiny-pilot/ansible-role-tinypilot)
[![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

Ansible role for [TinyPilot KVM](https://github.com/tiny-pilot/tinypilot).

## Role Variables

Available variables are listed below, along with default values (see [defaults/main.yml](defaults/main.yml)):

```yaml
tinypilot_interface: "127.0.0.1"
tinypilot_port: 8000
tinypilot_keyboard_interface: /dev/hidg0
# The client is responsible for specifying the path/URL to the TinyPilot Debian
# package
tinypilot_debian_package_path: null
```

## Dependencies

- [tiny-pilot.ustreamer](https://github.com/tiny-pilot/ansible-role-ustreamer)
- [tiny-pilot.nginx](https://github.com/tiny-pilot/ansible-role-nginx)

## Example Playbook

## Building a TinyPilot Debian package

To install TinyPilot using the Ansible role, you need to provide the role with a path or URL to a TinyPilot Debian package.

To build a TinyPilot Debian package, run the following snippet:

```bash
cd $(mktemp -d) && \
  git clone https://github.com/tiny-pilot/tinypilot.git . && \
  ./dev-scripts/build-debian-pkg
```

This will produce a TinyPilot Debian package under `./debian-pkg/releases`.

### `example.yml`

```yaml
- hosts: all
  roles:
    - role: ansible-role-tinypilot
      vars:
        tinypilot_debian_package_path: /path/to/tinypilot.deb
```

### Running Example Playbook

```bash
ansible-galaxy install git+https://github.com/tiny-pilot/ansible-role-tinypilot.git
ansible-playbook example.yml
```

## Documentation

- [Introduction to the USB gadget driver](docs/usb-gadget-driver.md)

## License

MIT

## Author Information

This role was created in 2020 by [Michael Lynch](http://mtlynch.io).
