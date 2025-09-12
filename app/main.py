#!/usr/bin/env python3

import datetime
import logging
import os

import flask
import flask_wtf
from werkzeug import exceptions

# We’re importing the log package first because it needs to overwrite the
# app-wide logger class before any other module loads it.
import log
import api
import db.settings
import db_connection
import json_response
import license_notice
import secret_key
import socket_api
import views
from find_files import find as find_files

host = os.environ.get('HOST', '127.0.0.1')
port = int(os.environ.get('PORT', 48000))
debug = 'DEBUG' in os.environ
use_reloader = os.environ.get('USE_RELOADER', '0') == '1'

root_logger = log.create_root_logger(flask.logging.default_handler)
if debug:
    root_logger.setLevel(logging.DEBUG)
else:
    root_logger.setLevel(logging.INFO)
    # Socket.io logs are too chatty at INFO level.
    logging.getLogger('socketio').setLevel(logging.ERROR)
    logging.getLogger('engineio').setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.info('Starting app')

app = flask.Flask(__name__, static_url_path='')
app.config.update(
    REMEMBER_COOKIE_HTTPONLY=True,
    SECRET_KEY=secret_key.get_or_create(),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=90),
    TEMPLATES_AUTO_RELOAD=True,
    WTF_CSRF_TIME_LIMIT=None,
)

# Configure cookie security.
with app.app_context():
    is_session_cookie_secure = (not debug and
                                db.settings.Settings().requires_https())
    app.config.update(SESSION_COOKIE_SECURE=is_session_cookie_secure)

# Configure CSRF protection.
csrf = flask_wtf.csrf.CSRFProtect(app)

app.register_blueprint(api.api_blueprint)
app.register_blueprint(license_notice.blueprint)
app.register_blueprint(views.views_blueprint)


@app.before_request
def check_proxy_https_redirect():
    """Checks whether the client has connected with HTTPS and handles redirect.

    The upstream proxy (in production) must set the `X-Forwarded-Proto` header
    to either `http` or `https`. In development there is no proxy, so we skip
    this mechanism locally.
    """
    if flask.current_app.debug:
        return None

    proxy_protocol = flask.request.headers.get('X-Forwarded-Proto')
    if not proxy_protocol:
        return flask.Response(
            'Request is missing required X-Forwarded-Proto header', status=400)

    settings = db.settings.Settings()
    if settings.requires_https() and proxy_protocol != 'https':
        redirect_url = flask.request.url.replace(f'{proxy_protocol}://',
                                                 'https://', 1)
        logger.info('Redirecting %s request to HTTPS: %s',
                    proxy_protocol.upper(), redirect_url)
        return flask.redirect(redirect_url, code=307)

    return None


@app.teardown_appcontext
def close_connection(_):
    db_connection.close()


@app.errorhandler(flask_wtf.csrf.CSRFError)
def handle_csrf_error(error):
    return json_response.error(error), 403


@app.after_request
def after_request(response):
    # Disable caching in debug mode.
    if debug:
        response.headers['Cache-Control'] = (
            'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0')
        response.headers['Expires'] = 0
        response.headers['Pragma'] = 'no-cache'
    return response


@app.errorhandler(Exception)
def handle_error(e):
    logger.exception(e)
    code = 500
    if isinstance(e, exceptions.HTTPException):
        code = e.code
    return json_response.error(e), code


def main():
    socketio = socket_api.socketio
    socketio.init_app(app)
    socketio.run(app,
                 host=host,
                 port=port,
                 debug=debug,
                 use_reloader=use_reloader,
                 extra_files=find_files.all_frontend_files())


if __name__ == '__main__':
    main()
