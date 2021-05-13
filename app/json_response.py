import flask


# The default dictionary is okay because we're not modifying it.
# pylint: disable=dangerous-default-value
def success(data={}):
    """A JSON response for a successful request.

    Args:
        data: Dictionary with JSON properties to include.

    Returns:
        A `flask.Response` object with JSON body containing the serialized data.
    """
    return flask.jsonify(data)


def error(original_error):
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
