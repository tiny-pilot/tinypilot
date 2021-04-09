import dataclasses
import json


@dataclasses.dataclass
class Result:
    error: str


def read(result_file):
    """Reads an update result file.

    Parses the contents of a result file into a Result object. The file should
    have a format like:

      {
        "error": ""
      }

    Args:
        result_file: A file containing JSON-formatted results of an update job.

    Returns:
        A Result object parsed from the file.
    """
    raw_result = json.load(result_file)
    return Result(error=raw_result.get('error', ''))


def write(result, result_file):
    """Serializes a Result object to a file as JSON.

    Args:
        result: A Result object containing results of an update job.
        result_file: File handle to which to serialize the result object.
    """
    json.dump(dataclasses.asdict(result), result_file)
