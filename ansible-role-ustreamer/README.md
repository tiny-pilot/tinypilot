# Ansible Role: µStreamer

[![License](https://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

Ansible role for [µStreamer](https://github.com/tiny-pilot/ustreamer).

Installs µStreamer via a Debian package and enables it as a systemd service.

## Role Variables

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
ansible-playbook example.yml
```

## License

MIT

## Author Information

This role was created in 2020 by [TinyPilot](https://tinypilotkvm.com).
