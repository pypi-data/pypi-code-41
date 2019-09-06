from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from .config import get_config_by_env


class FlaskFactory:

    def __init__(self, env='dev'):
        self.config = get_config_by_env(env)

    def initiallize_flask(self, db, blueprint_dicts):
        app = Flask(__name__)
        app.config.from_object(self.config)
        with app.app_context() as ctx:
            ctx.push()
            db.init_app(app)
        for blueprint_dict in blueprint_dicts:
            bp = blueprint_dict.pop('bp')
            app.register_blueprint(bp, **blueprint_dict)
        return app

    @staticmethod
    def create_db():
        db = SQLAlchemy()
        return db
