import platform
import subprocess


class Error(Exception):
    pass


class CannotDetermineHostnameError(Error):
    pass


class HostnameChangeError(Error):
    pass


def determine():
    """Determines the hostname of the machine.

    Returns:
        The hostname as string. Note that this is the hostname which is
        currently effective, so it doesn’t reflect potential pending changes
        in `/etc/hostname`.

    Raises:
        CannotDetermineHostnameError: If the hostname cannot be obtained from
            the system.
    """
    hostname = platform.node()  # Returns empty string on failure.
    if hostname == '':
        raise CannotDetermineHostnameError('Cannot determine hostname')
    return hostname


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
