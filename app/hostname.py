import dataclasses
import platform
import subprocess

_ETC_HOSTNAME_FILE_PATH = '/etc/hostname'


class Error(Exception):
    pass


class CannotDetermineHostnameError(Error):
    pass


class HostnameChangeError(Error):
    pass


@dataclasses.dataclass
class Hostname:
    """Represents information about the machine’s hostname. Contains the
    currently active hostname as well as the one that is configured. Normally
    these should be the same, but they might differ when a change is still
    pending (i.e. if the machine is yet to be rebooted after having changed
    the hostname).
    """
    current: str
    configured: str


def determine():
    """Determines the hostname of the machine.

    Returns:
        A hostname object as described in `Hostname`.

    Raises:
        CannotDetermineHostnameError: If the hostname cannot be obtained from
            the system.
    """
    current = platform.node()  # Returns empty string on failure.
    if current == '':
        raise CannotDetermineHostnameError('Cannot determine hostname')

    try:
        with open(_ETC_HOSTNAME_FILE_PATH) as file:
            configured = parse_etc_hostname(file.read())
        return Hostname(current, configured)
    except Exception as e:
        raise CannotDetermineHostnameError('Cannot read configuration file: ' +
                                           str(e)) from e


def change(new_hostname):
    """Changes the hostname of the machine.

    This populates the new name to the configuration files. The change will
    only come into effect after system reboot.

    Args:
        new_hostname: The new hostname as string.
    """
    try:
        return subprocess.check_output(
            ['/opt/tinypilot-privileged/change-hostname', new_hostname],
            stderr=subprocess.STDOUT,
            universal_newlines=True)
    except subprocess.CalledProcessError as e:
        raise HostnameChangeError(str(e.output).strip()) from e
    except Exception as e:
        raise HostnameChangeError(str(e)) from e


def parse_etc_hostname(file_contents: str):
    """Parses the file contents of an `/etc/hostname` file and
    obtains the hostname.

    According to https://manpages.debian.org/stretch/systemd/hostname.5.en.html
    a hostname file can contain line comments (lines starting with a `#`
    character).

    Returns:
        The hostname as string.
    """
    for line in file_contents.splitlines():
        text = line.strip()
        if text.startswith('#') or not text:
            continue
        return text
