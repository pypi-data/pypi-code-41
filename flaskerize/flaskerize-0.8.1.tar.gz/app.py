import os
from flask import Flask


def create_app():
    from _fz_bp import site
    app = Flask(__name__, static_folder=None)
    app.register_blueprint(site, url_prefix='/')

    @app.route("/")
    @app.route("/health")
    def serve():
        return "app online!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run()