import subprocess


class Error(Exception):
    pass


class LogCollectionScriptFailed(Error):
    pass


def collect():
    """Collects and aggregates contents of TinyPilot-related logs and files.

    Returns:
        A large string with the full contents of TinyPilot's debug logs and
        configuration files.
    """
    try:
        return subprocess.check_output(
            ['/opt/tinypilot-privileged/collect-debug-logs', '-q'])
    except subprocess.CalledProcessError as e:
        raise LogCollectionScriptFailed(str(e)) from e
