from .factory import FlaskFactory
from .views import obx
from .models import db


def get_app():
    factory = FlaskFactory()
    
    blueprint_dicts = [
            dict(
                bp=obx,
            )
        ]
    
    app = factory.initiallize_flask(db, blueprint_dicts)
    return app
