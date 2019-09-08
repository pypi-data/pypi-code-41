from flask import Blueprint

bp = Blueprint('errors', __name__)

from ps_herald.errors import handlers
