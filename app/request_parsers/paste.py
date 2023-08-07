from request_parsers import json


def parse_text(request):
    """
    Parses the text and browser language properties from the request.

    Args:
        request: Flask request with the following fields in the JSON body:
            (str) text
            (str) language

    Returns:
        A two-tuple consisting of the parsed text and language.
    """
    # pylint: disable=unbalanced-tuple-unpacking
    (text,
     language) = json.parse_json_body(request,
                                      required_fields=['text', 'language'])

    return text, language
