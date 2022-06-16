from request_parsers import errors


def parse_json_body(request, required_fields):
    """Parse a request with a JSON payload.

    Args:
      request: A flask.Request object that caller expects to carry a JSON
        dictionary payload.
      required_fields: A list of required fields in the JSON payload.

    Returns:
      The parsed field values as tuple. The arity and order of the tuple
      matches that of the `required_fields` argument.
    """
    json = request.get_json()

    if not isinstance(json, dict):
        raise errors.MalformedRequestError(
            'Request is invalid, expecting a JSON dictionary')

    result = []
    for field in required_fields:
        if field not in json:
            raise errors.MissingFieldError(f'Missing required field: {field}')
        result.append(json[field])

    return tuple(result)
