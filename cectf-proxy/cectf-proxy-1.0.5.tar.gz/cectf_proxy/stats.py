from .celery import app
from .database import Request, Response, Session
from mongoengine import connect


def handle_request(request_id, request):
    print("REQUESTO")
    print(dir(request))
    kwargs = {
        'method': request.method,
        'url': request.url,
        'headers': [k for k in request.headers.items()],
        'cookies': request.cookies,
        'remote_addr': request.remote_addr,
        # 'date': request.date
    }
    if request.is_json:
        kwargs['json'] = request.json
    return request_task.delay(request_id, kwargs)


def handle_response(request_id, response):
    kwargs = {
        'status_code': response.status_code,
        'headers': response.raw.headers.items()}
    if response.headers['Content-Type'] == "application/json":
        kwargs['json'] = response.json()
    return response_task.delay(request_id, kwargs)


@app.task
def request_task(request_id, kwargs):
    connect('test')
    print("(%s) Requesting %s" % (request_id, kwargs))
    request = Request(**kwargs)
    request.save()
    return kwargs


@app.task
def response_task(request_id, kwargs):
    connect('test')
    print("(%s) Responsing %s" % (request_id, kwargs))
    response = Response(**kwargs)
    response.save()
    return kwargs
