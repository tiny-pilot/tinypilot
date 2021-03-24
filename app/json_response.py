import flask


# The default dictionary is okay because we're not modifying it.
# pylint: disable=dangerous-default-value
def success(fields={}):
    """A JSON response for a successful request.

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
    """A JSON response for a failed request.

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
