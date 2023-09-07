import dataclasses
import multiprocessing
import typing


@dataclasses.dataclass
class ProcessResult:
    return_value: typing.Any = None
    exception: Exception = None

    def was_successful(self) -> bool:
        return self.exception is None


class ProcessWithResult(multiprocessing.Process):
    """A multiprocessing.Process object that keeps track of the child process'
    result (i.e., the return value and exception raised).

    Inspired by:
    https://stackoverflow.com/a/33599967/3769045
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create the Connection objects used for communication between the
        # parent and child processes.
        self.parent_conn, self.child_conn = multiprocessing.Pipe()

    def run(self):
        """Method to be run in sub-process."""
        result = ProcessResult()
        try:
            if self._target:
                result.return_value = self._target(*self._args, **self._kwargs)
        except Exception as e:
            result.exception = e
            raise
        finally:
            self.child_conn.send(result)

    def result(self):
        """Get the result from the child process.

        Returns:
            If the child process has completed, a ProcessResult object.
            Otherwise, a None object.
        """
        return self.parent_conn.recv() if self.parent_conn.poll() else None
