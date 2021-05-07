import flask

# We are currently migrating from success/error to success2/error2.
# The former will be eventually removed and the latter renamed.


# The default dictionary is okay because we're not modifying it.
# pylint: disable=dangerous-default-value
def success(fields={}):
    """A JSON response for a successful request. (DEPRECATED, use `success2`)

    Args:
        fields: Dictionary with JSON properties to include.

    Returns:
        A `flask.Response` object with JSON body. The JSON structure contains a
        `success` property (which is `true`) and an `error` property (which is
        `null`). The additional fields given are merged into the JSON output.
    """
    response = {
        'success': True,
        'error': None,
    }
    for key, val in fields.items():
        response[key] = val
    return flask.jsonify(response)


def error(message):
    """A JSON response for a failed request. (DEPRECATED, use `error2`)

    Args:
        message: String containing the error message.

    Returns:
        A `flask.Response` object with JSON body. The JSON structure contains a
        `success` property (which is `false`) and an `error` property (which is
        a string containing the error message).
    """
    return flask.jsonify({
        'success': False,
        'error': message,
    })


# The default dictionary is okay because we're not modifying it.
# pylint: disable=dangerous-default-value
def success2(data={}):
    """A JSON response for a successful request.

    Args:
        data: Dictionary with JSON properties to include.

    Returns:
        A `flask.Response` object with JSON body containing the serialized data.
    """
    return flask.jsonify(data)


def error2(original_error):
    """A JSON response for a failed request.

    Args:
        original_error: The original error object

    Returns:
        A `flask.Response` object with JSON body. The JSON contains two fields:
        - message: A string with the error message.
        - code: Either a string with a unique error code as string, or `null`.
            This property is only set for errors that are handled explicitly by
            the TinyPilot frontend.
    """
    code = getattr(original_error, 'code', None)
    return flask.jsonify({
        'message': str(original_error),
        'code': code,
    })
