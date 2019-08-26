import json

from flask import Blueprint, jsonify, current_app

from oarepo_heartbeat import readiness_probe, liveliness_probe, environ_probe

blueprint = Blueprint('oarepo-heartbeat', __name__, url_prefix='/.well-known/heartbeat')


@blueprint.route('/readiness')
def readiness():
    data = [x[1] for x in readiness_probe.send(blueprint)]
    return _collect_results(*data)


@blueprint.route('/liveliness')
def liveliness():
    data = [x[1] for x in liveliness_probe.send(blueprint)]
    return _collect_results(*data)


@blueprint.route('/environ')
def environ():
    data = {}
    total_status = True
    for x in environ_probe.send(blueprint):
        status, values = x[1]
        total_status &= status
        data.update(values)
    return current_app.response_class(json.dumps({
        'status': total_status,
        **data
    }))


def _collect_results(*values):
    total_status = True
    checks = {}
    for name, status, data in values:
        total_status &= status
        checks[name] = {
            **data,
            'status': status
        }
    return current_app.response_class(json.dumps({
        'status': total_status,
        'checks': checks
    }), status=200 if total_status else 500)
