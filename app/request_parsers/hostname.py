from request_parsers import message as message_parser


def parse_hostname(request):
    message = message_parser.parse_message(request, ['hostname'])
    return message['hostname']
