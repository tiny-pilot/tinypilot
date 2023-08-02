from request_parsers import json


def parse_text(request):
    # pylint: disable=unbalanced-tuple-unpacking
    (text,
     language) = json.parse_json_body(request,
                                      required_fields=['text', 'language'])

    return text, language
