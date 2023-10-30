from flask import Blueprint

import db.settings

# For invoking the commands on the CLI you need to specify the FLASK_APP env
# variable containing the path to the main file. E.g.: FLASK_APP=app/main.py
cli_blueprint = Blueprint('cli', __name__)


@cli_blueprint.cli.command('streaming-mode')
def streaming_mode():
    """Prints TinyPilot's preferred video streaming mode, either H264 or MJPEG.

    Note: this doesn't represent the currently active video streaming mode
    because H264 can fail and fallback to MJPEG.

    Example of invocation:
        flask cli streaming-mode
    """
    print(db.settings.Settings().get_streaming_mode().value)
