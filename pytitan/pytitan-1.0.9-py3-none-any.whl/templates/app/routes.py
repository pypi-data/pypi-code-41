# -*- coding: utf-8 -*-
from flask import Blueprint, request, current_app, json
import datetime

bp = Blueprint(__name__, 'home')


@bp.route("/health-check")
def health_check():
    return datetime.datetime.timestamp()
