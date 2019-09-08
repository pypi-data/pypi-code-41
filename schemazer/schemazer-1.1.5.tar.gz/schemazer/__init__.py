from functools import wraps
from flask import abort, request
from flask_classy import route

from schemazer.helpers import remote_addr
from schemazer.commons.errors import RequestErrors
from schemazer.config import SchemazerConfig
from schemazer.validator import RequestValidator


class QueryMeta:
    ip = None
    token = None
    cookies = None
    headers = None
    apikey = None


class Query:
    def __init__(self):
        self.meta = QueryMeta()
        self.args = {}

    def to_dict(self):
        return (f'==========request===========\n'
                f'ip: {self.meta.ip}\n'
                f'token: {self.meta.token}\n'
                f'cookies: {self.meta.cookies}\n'
                f'headers: {self.meta.headers}\n'
                f'args: {self.args}\n')


class Schemazer:
    def __init__(self, app, schema):
        self.schema = schema
        self.config = SchemazerConfig()
        app.schemazer = self

        for param in [x for x in dir(SchemazerConfig) if
                      not x.startswith('_')]:
            name = 'SCHEMAZER_' + param
            setattr(self.config, param,
                    app.config.get(name, getattr(self.config, param)))

    def route(self, schema=None, path=None):
        def decorator(f):
            @route(path if path else schema.path, methods=schema.methods)
            @wraps(f)
            def decorated_function(*args, **kwargs):
                """
                Create Query object from flask request.
                :return Query: Request with auth data.
                """
                request.query = Query()

                if request.method == 'GET':
                    request.query.args.update(request.args.to_dict(flat=True))
                if request.method == 'POST':
                    data = request.get_json() or dict()
                    if not isinstance(data, dict):
                        abort(RequestErrors.BadRequest.json_abort())
                    request.query.args.update(data)

                request.query.meta.token = (
                        request.query.args.get(self.config.QUERY_TOKEN) or
                        request.headers.get(self.config.HEADER_TOKEN) or
                        request.cookies.get(self.config.COOKIE_TOKEN)
                )
                request.query.meta.apikey = (
                        request.query.args.get(self.config.QUERY_APIKEY) or
                        request.headers.get(self.config.HEADER_APIKEY) or
                        request.cookies.get(self.config.COOKIE_APIKEY)
                )
                request.query.meta.ip = remote_addr(request)
                request.query.meta.cookies = request.cookies
                request.query.meta.headers = request.headers

                request_validator = RequestValidator()
                result = request_validator.process(schema.parameters)
                if result is not True:
                    return result

                return f(*args, **kwargs)
            return decorated_function
        return decorator
