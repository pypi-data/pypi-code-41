from flask import Blueprint

bp = Blueprint('main', __name__)

from ps_herald.main import routes
