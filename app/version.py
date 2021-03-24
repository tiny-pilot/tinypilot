import git


class Error(Exception):
    pass


class GitError(Error):
    pass


def local_version():
    try:
        return git.local_head_commit_id()
    except git.Error as e:
        raise GitError('Failed to check local version: %s' % str(e)) from e


def latest_version():
    try:
        return git.remote_head_commit_id()
    except git.Error as e:
        raise GitError('Failed to check latest available version: %s' %
                       str(e)) from e
