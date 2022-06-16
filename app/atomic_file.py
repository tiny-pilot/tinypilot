import contextlib
import errno
import logging
import os
import shutil
import tempfile

logger = logging.getLogger(__name__)

# Folder path where the temporary files are created. `None` means that it
# falls back to the system’s default path for temporary files, e.g. `/tmp`.
# This variable is only used for the purpose of patching the path in the tests.
_TEMP_FOLDER = None


@contextlib.contextmanager
def create(file_path, chmod_mode=0o600):
    """Creates a new file in an atomic way.

    It creates the file in the temporary folder first until the caller has
    finished providing all file contents. Only then, it moves the file to the
    destination. It always will clean up the temporary file properly.

    Args:
        file_path: The absolute path of the file (str).
        chmod_mode: File permissions as bitfield, as used by `os.chmod`. It
            defaults to 0o600 (-rw------).

    Raises:
        OSError if disk operations fail.

    Returns:
        A stream that can be written into.
    """
    file_descriptor, temp_file = tempfile.mkstemp(dir=_TEMP_FOLDER)
    try:
        with open(temp_file, 'bw') as file:
            yield file
        os.chmod(temp_file, chmod_mode)
        shutil.move(temp_file, file_path)
    finally:
        os.close(file_descriptor)
        _remove_if_exists(temp_file)


def _remove_if_exists(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        if e.errno == errno.ENOENT:  # No such file or directory
            pass
        else:
            logger.warning('Unexpected error while removing file: %s', str(e))
