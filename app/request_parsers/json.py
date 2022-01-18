from request_parsers import errors


def parse_json_body(request, required_fields):
    """Parse a message with a JSON payload.

    Args:
      request: A flask.Request object that caller expects to carry a JSON
        dictionary payload.
      required_fields: A list of required fields in the message dictionary.

    Returns:
      The parsed field values as tuple. The arity and order of the tuple
      matches that of the `required_fields` argument.
    """
    message = request.get_json()

    if not isinstance(message, dict):
        raise errors.MalformedRequestError(
            'Request is invalid, expecting a JSON dictionary')

    result = []
    for field in required_fields:
        if field not in message:
            raise errors.MissingFieldError('Missing required field: %s' % field)
        result.append(message[field])

    return tuple(result)
