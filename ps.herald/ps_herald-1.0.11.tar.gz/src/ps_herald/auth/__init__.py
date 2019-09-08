from flask import Blueprint

bp = Blueprint('auth', __name__)

from ps_herald.auth import routes
