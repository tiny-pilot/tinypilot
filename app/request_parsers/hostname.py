from request_parsers import errors
from request_parsers import message as message_parser
from request_parsers.validators import hostname as hostname_validator


def parse_hostname(request):
    message = message_parser.parse_message(request,
                                           required_fields=['hostname'])
    hostname = message['hostname']
    if not hostname_validator.validate(hostname):
        raise errors.InvalidHostnameError(
            'The hostname contains invalid characters.')
    return hostname
