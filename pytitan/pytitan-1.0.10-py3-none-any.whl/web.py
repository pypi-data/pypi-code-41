# -*- coding: utf-8 -*-
import base64
import os
from flask import Flask as _Flask, request, json, jsonify,current_app
from flask.json import JSONEncoder as _JSONEncoder
from datetime import date
from bson import ObjectId
from werkzeug.exceptions import InternalServerError, HTTPException


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if hasattr(o, 'keys') and hasattr(o, '__getitem__'):
            return dict(o)
        if isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        if isinstance(o, ObjectId):
            return str(o)
        raise InternalServerError("对象序列发时发生不可预期的错误")


class Flask(_Flask):
    """
    修复中文序列化时的乱码
    """
    json_encoder = JSONEncoder


def get_token():
    headers = request.headers
    jwt = headers['AUTHORIZATION'].split(' ')[1]
    data = base64.urlsafe_b64decode(jwt.split(".")[1] + '=' * (4 - len(jwt.split(".")[1]) % 4))
    return json.loads(data)


def result(result=None, success=True, message=u'成功'):
    """
    返回JSON化的结果集
    :param result:
    :param success:
    :param message:
    :return:
    """
    return jsonify({'success': success,
                    'message': message,
                    'result': result if result is not None else {}})


def fail(message=u'失败'):
    """
    返回错误的JSON化结果集
    :param message:
    :return:
    """
    return result(message=message, success=False)


def create_flask(name, default_blueprint=None):
    app = Flask(name, instance_relative_config=True)
    app.config.from_object('config.' + os.environ['FLASK_ENV'])
    app.config.from_pyfile('config.py')
    if default_blueprint is not None:
        app.register_blueprint(default_blueprint, url_prefix='/')
    app.register_error_handler(500, flask_error_handler)
    return app


def flask_error_handler(e):
    current_app.logger.exception(e)
    response = e.get_response()
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "msg": e.description,
    })
    response.content_type = "application/json"
    return response


