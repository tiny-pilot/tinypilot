COMMANDS = {}


def command(command_name):

    def decorator(func):
        COMMANDS[command_name] = func
        return func

    return decorator
