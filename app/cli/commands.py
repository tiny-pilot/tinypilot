import db.settings
from cli.registry import command


@command('streaming-mode')
def streaming_mode(_args):
    """Prints the currently applicable streaming mode."""
    mode = db.settings.Settings().get_streaming_mode().value
    print(mode)
