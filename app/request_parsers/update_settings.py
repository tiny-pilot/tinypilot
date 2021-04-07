from request_parsers import message as message_parser


def parse_settings(request):
    return message_parser.parse_message(request, [])
