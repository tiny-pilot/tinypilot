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


def with_timeout(seconds, function, *args, **kwargs):
    """Executes a function in a child process with a specified timeout.

    Args:
        seconds: The execution time limit in seconds.
        function: The function to be executed in a child process.
        *args: Optional `function` arguments.
        **kwargs: Optional `function` keyword argument.
    
    Returns:
        The return value of the `function`.

    Raises:
        TimeoutError: If the execution time of the `function` exceeds the
            timeout `seconds`.
    """
    process = ProcessWithResult(target=function,
                                args=args,
                                kwargs=kwargs,
                                daemon=True)
    process.start()
    process.join(timeout=seconds)
    if process.is_alive():
        process.kill()
        _wait_for_process_exit(process)
    result = process.result()
    if result is None:
        raise TimeoutError(f'Process failed to complete in {seconds} seconds')
    if not result.was_successful():
        raise result.exception
    return result.return_value


def _wait_for_process_exit(target_process):
    max_attempts = 3
    for _ in range(max_attempts):
        target_process.join(timeout=0.1)
