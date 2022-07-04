import json

from request_parsers import errors


def parse_json_body(response, required_fields):
    """Parse an HTTP response with a JSON payload.

    Args:
      response: A http.client.HTTPResponse object that caller expects to carry
        a JSON dictionary payload.
      required_fields: A list of required fields in the JSON payload.

    Returns:
      The parsed field values as tuple. The arity and order of the tuple
      matches that of the `required_fields` argument.
    """
    json_data = json.loads(response.read().decode())

    if not isinstance(json_data, dict):
        raise errors.MalformedRequestError(
            'Response is invalid, expecting a JSON dictionary')

    result = []
    for field in required_fields:
        if field not in json_data:
            raise errors.MissingFieldError('Missing required field: %s' % field)
        result.append(json_data[field])

    return tuple(result)
