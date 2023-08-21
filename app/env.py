import os
import pathlib

_TINYPILOT_HOME_DIR = os.environ.get('TINYPILOT_HOME_DIR', '/home/tinypilot')


def abs_path_in_home_dir(relative_path):
    """Resolves the full, absolute path for an object in the tinypilot home dir.

    Always use this helper function instead of relying on the ~ alias or the
    $HOME environment variable, in order to stay agnostic of the app’s execution
    context.

    In production, $HOME is always supposed to point to /home/tinypilot, but it
    might differ in a local development environment, or when invoking the app
    via sudo (e.g., when running a privileged script). In order to avoid
    surprising behavior in such scenarios, we have hardcoded the path to be on
    the safe side.

    Args:
        relative_path: The path of a file or folder relative to the tinypilot
            home dir, without leading slash (as string).

    Returns:
        The eventual, absolute path (as string).
    """
    return str(pathlib.Path(_TINYPILOT_HOME_DIR).joinpath(relative_path))
