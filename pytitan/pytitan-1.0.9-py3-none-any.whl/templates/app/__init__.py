# -*- coding: utf-8 -*-
from .routes import bp
from titan.web import create_flask


def create_app():
    app = create_flask(__name__, bp)
    # 此处可始化插件
    return app
