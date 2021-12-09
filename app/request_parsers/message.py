from request_parsers import errors


# This helper function is only needed during the migration.
def _process_message(request, required_fields):
    message = request.get_json()

    if not isinstance(message, dict):
        raise errors.MalformedRequestError(
            'Request is invalid, expecting a JSON dictionary')

    result = []
    for field in required_fields:
        if field not in message:
            raise errors.MissingFieldError('Missing required field: %s' % field)
        result.append(message[field])

    return message, result


def parse_message(request, required_fields):
    """Parse a message with a JSON payload. DEPRECATED – use `parse_json_body`.

    Args:
      request: A flask.Request object that caller expects to carry a JSON
        dictionary payload.
      required_fields: A list of required fields in the message dictionary.

    Returns:
      The parsed message as a dictionary of its JSON payload.
    """
    message, _ = _process_message(request, required_fields)
    return message


def parse_json_body(request, required_fields):
    _, required_fields = _process_message(request, required_fields)
    return tuple(required_fields)
