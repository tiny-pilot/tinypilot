import git


class Error(Exception):
    pass


class GitError(Error):
    pass


def local_version():
    try:
        return git.local_head_commit_id()
    except git.Error as e:
        raise GitError(f'Failed to check local version: {str(e)}') from e


def latest_version():
    try:
        return git.remote_head_commit_id()
    except git.Error as e:
        raise GitError(
            f'Failed to check latest available version: {str(e)}') from e
