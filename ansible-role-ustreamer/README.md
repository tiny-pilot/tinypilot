# Ansible Role: µStreamer

[![CircleCI](https://circleci.com/gh/tiny-pilot/ansible-role-ustreamer.svg?style=svg)](https://circleci.com/gh/tiny-pilot/ansible-role-ustreamer) [![License](http://img.shields.io/:license-mit-blue.svg?style=flat-square)](LICENSE)

Ansible role for [µStreamer](https://github.com/pikvm/ustreamer).

Compiles µStreamer from source and installs it as a systemd service.

## Role Variables

Available variables are listed below, along with default values (see [defaults/main.yml](defaults/main.yml)):

```yaml
ustreamer_group: ustreamer
ustreamer_user: ustreamer
ustreamer_dir: /opt/ustreamer
ustreamer_repo: https://github.com/pikvm/ustreamer.git
ustreamer_repo_version: master
```

For a full list of options, see [defaults/main.yml](https://github.com/tiny-pilot/ansible-role-ustreamer/blob/master/defaults/main.yml).

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
ansible-galaxy install git+https://github.com/tiny-pilot/ansible-role-ustreamer.git
ansible-playbook example.yml
```

## License

MIT

## Author Information

This role was created in 2020 by [TinyPilot](https://tinypilotkvm.com).
