import flask

import local_system

api_blueprint = flask.Blueprint('api', __name__, url_prefix='/api')


@api_blueprint.route('/shutdown', methods=['POST'])
def shutdown_post():
    try:
        local_system.shutdown()
        return flask.jsonify({
            'success': True,
            'error': None,
        })
    except local_system.Error as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500


@api_blueprint.route('/restart', methods=['POST'])
def restart_post():
    try:
        local_system.restart()
        return flask.jsonify({
            'success': True,
            'error': None,
        })
    except local_system.Error as e:
        return flask.jsonify({
            'success': False,
            'error': str(e),
        }), 500
