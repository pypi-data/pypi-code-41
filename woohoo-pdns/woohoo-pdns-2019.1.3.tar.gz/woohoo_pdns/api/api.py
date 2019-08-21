# -*- encoding: utf-8 -*-

import json

from flask import Blueprint, request, current_app
from flask_httpauth import HTTPBasicAuth

from .db import get_db


bp = Blueprint('api', __name__, url_prefix='/api')
auth = HTTPBasicAuth()

@bp.route("/q/<string:q>")
@auth.login_required
def query(q):
    """
    The method supporting the query API endpoint.

    Args:
        q (str): The term to search for (use '*' as wildcard).

    Returns:
        A JSON structure compatible with the `Passive DNS - Common Output Format`_.

        An example::

            [
                {
                    "hitcount": 7,
                    "time_first": 1559245077.432,
                    "time_last": 1559245077.432,
                    "rrtype": 5,
                    "rrname": "www.icloud.com.edgekey.net",
                    "rdata": "e4478.a.akamaiedge.net."
                }
            ]

        .. _Passive DNS - Common Output Format: http://tools.ietf.org/html/draft-dulaunoy-dnsop-passive-dns-cof-01
    """
    try:
        rdata = int(request.args.get("rdata"))
        print("rdata: {}".format(rdata))
        if not rdata:
            rdata = False
        else:
            rdata = True
    except ValueError:
        rdata = False
    except TypeError:
        rdata = False
    d = get_db()
    r = d.query(q, rdata)
    r_json = [json.dumps(rec.to_jsonable()) for rec in r]
    res_json = "[{}]".format(", ".join(r_json))
    return res_json


@bp.route("/count")
@auth.login_required
def count():
    """
    The method supporting the count API endpoint. It just returns the number of records in the database.

    Returns:
        The number of entries in the database (as string).
    """
    d = get_db()
    r = d.count
    res_json = json.dumps(r)
    return res_json


@bp.route("/recent")
@auth.login_required
def most_recent():
    """
    The method supporting the recent API endpoint. It returns the most recent entry from the database.

    For example like this::

        {
            "hitcount": 56,
            "time_first": 1559244767.913,
            "time_last": 1559245313.506,
            "rrtype": 1,
            "rrname": "prod-cc-asn-20190411-1321-nlb-19436c10e4427871.elb.us-east-1.amazonaws.com",
            "rdata": "3.208.62.22"
        }
    """
    d = get_db()
    r = d.most_recent
    return json.dumps(r.to_jsonable())


@auth.verify_password
def verify_password(username, password):
    """
    Check if a valid API key was provided.

    Called by :mod:`flask_httpauth` when authentication is required. As woohoo pDNS is 'misusing' ``flask_httpauth`` to
    avoid reinventing the wheel, ``username`` and ``password`` will always be empty (we do *not* use basic
    authentication).

    The API key must be provided in a header called ``Authorization`` and have the following format::

        "Authorization: <API key as configured in config file>"

    Args:
        username (str): Ignored (would be the username for basic authentication).
        password (str): Ignored (would be the password for basic authentication).
    """
    try:
        token = request.headers["Authorization"].split(" ")[-1]
    except KeyError:
        token = None
    current_app.logger.debug("Checking API key '{}'".format(token))
    current_app.logger.debug("Valid keys '{}'".format(current_app.config["API_KEYS"]))
    current_app.logger.debug("(username: '{}', password: '{}')".format(username, password))
    return token in current_app.config["API_KEYS"]
