
import requests
from flask import Blueprint, current_app, request, Response, session
from . import stats


def _proxy(new_url):
    new_url = request.url.replace(request.host_url, new_url + "/")
    print("Proxying", request.method, request.url, "to", new_url)
    #stats.handle_request(hash(request), request)
    resp = requests.request(
        method=request.method,
        url=new_url,
        headers={key: value for (key, value)
                 in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding',
                        'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    #stats.handle_response(hash(request), resp)
    response = Response(resp.content, resp.status_code, headers)
    return response


static_bp = Blueprint("static_routes", __name__, url_prefix="/")


@static_bp.route('/')
@static_bp.route('/<path:path>')
def frontend(path=None):
    print("current session: ", session)
    return _proxy(current_app.config.get('CECTF_FRONTEND_URL'))


api_bp = Blueprint("api_routes", __name__, url_prefix="/")


@api_bp.route('/api/<path:path>', methods=('GET', 'POST', 'DELETE'))
def api(path):
    return _proxy(current_app.config.get('CECTF_SERVER_URL'))


def init_app(app):
    app.register_blueprint(static_bp)
    app.register_blueprint(api_bp)
