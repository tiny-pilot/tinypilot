# Ansible Role: µStreamer

[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

Ansible role for [µStreamer](https://github.com/tiny-pilot/ustreamer).

Installs µStreamer via a Debian package and enables it as a systemd service.

## Role Variables

Required variables are listed below:

```yaml
# Specifies the filesystem path or URL of a Debian package that installs
# uStreamer.
ustreamer_debian_package_path: ustreamer_0.0-00000000000000_armhf.deb
```

For a full list of options, see [defaults/main.yml](defaults/main.yml).

## Dependencies

None

## Example Playbook

#### `example.yml`

```yaml
- hosts: all
  roles:
    - role: ansible-role-ustreamer
```

### Running Example Playbook

```bash
USTREAMER_DEBIAN_PACKAGE='ustreamer_0.0-00000000000000_armhf.deb'

ansible-playbook \
  example.yml \
  --extra-vars "ustreamer_debian_package_path=${USTREAMER_DEBIAN_PACKAGE}"
```

## License

MIT

## Author Information

This role was created in 2020 by [TinyPilot](https://tinypilotkvm.com).
