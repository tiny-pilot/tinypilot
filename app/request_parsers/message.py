from request_parsers import errors


def parse_message(request, required_fields):
    """Parse a message with a JSON payload.

    Args:
      request: A flask.Request object that caller expects to carry a JSON
        dictionary payload.
      required_fields: A list of required fields in the message dictionary.

    Returns:
      The parsed message as a dictionary of its JSON payload.
    """
    message = request.get_json()

    if not isinstance(message, dict):
        raise errors.MalformedRequestError(
            'Request is invalid, expecting a JSON dictionary')

    for field in required_fields:
        if field not in message:
            raise errors.MissingFieldError('Missing required field: %s' % field)

    return message
