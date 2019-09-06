import json
from flask import Blueprint, request


obx = Blueprint('obx', __name__)


@obx.route('/')
def root_view():
    return 'Hello World'
