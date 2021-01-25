import subprocess


class Error(RuntimeError):
    pass


def collect():
    """Collects debug logs by running the collect-debug-logs script."""
    try:
        script_path = '/opt/tinypilot-privileged/collect-debug-logs'
        return subprocess.check_output([script_path, '-q'])
    except subprocess.CalledProcessError as e:
        return Error(str(e))
