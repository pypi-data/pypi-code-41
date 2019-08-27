# -*- encoding: utf-8 -*-

import requests

from datetime import datetime, timezone
from dateutil import tz
from flask import Blueprint, request, flash, render_template, redirect, url_for, current_app

from .meta import types

bp = Blueprint('gui', __name__)


@bp.route("/", methods=('GET', 'POST'))
def index():
    """Renders the index page (i.e. the 'homepage')"""
    return render_template("index.html")


@bp.route("/q/", defaults={"q": None}, methods=['GET', 'POST'])
@bp.route("/q/<q>", methods=['GET'])
def query(q):
    """
    Queries the database and renders the result page.

    Args:
        q (str): The query string, can be text or an IP address (v4 or v6).

    Note:
        Uses the 'GET after POST' paradigm to avoid the 'do you want to
        re-submit the form' question of browsers.
    """
    error = None

    if request.method == 'POST':
        q = request.form.get("query")
        rdata = request.form.get("rdata")
        redirect_url = url_for("gui.query", q=q, rdata=rdata)
        current_app.logger.debug("GET after POST, redirecting to '{}'".format(redirect_url))
        return redirect(redirect_url)

    if not q:
        error = "no query to execute"
    rdata = request.args.get("rdata")

    current_app.logger.debug("Query: {}".format(q))
    current_app.logger.debug("Rdata: {}".format(rdata))

    if error is not None:
        flash(error)
    else:
        w_tz = tz.gettz(current_app.config["TIMEZONE"])
        # We use a header of the form "Authorization: Token <token_goes_here>" for authentication
        # similar to https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication
        headers = {'Authorization': "Token {}".format(current_app.config["API_KEY"])}
        api_query_url = "/".join([current_app.config["API_ENTRYPOINT"], "q", q])
        if rdata:
            api_query_url = "?".join([api_query_url, "rdata=1"])
        current_app.logger.debug("Executing query against API: {}".format(api_query_url))
        r = requests.get(api_query_url, headers=headers)
        if r.status_code == requests.codes.unauthorized:
            error = "no valid authorization to use woohoo pDNS API"
            flash(error)
        elif r.status_code == requests.codes.ok:
            r_j = r.json()
            for record in r_j:
                record["time_first"] = datetime.fromtimestamp(
                    record["time_first"], tz=timezone.utc).astimezone(w_tz).replace(microsecond=0)
                record["time_last"] = datetime.fromtimestamp(
                    record["time_last"], tz=timezone.utc).astimezone(w_tz).replace(microsecond=0)
                record["rrtype"] = types["T{}".format(record["rrtype"])]

            now = datetime.now(tz=w_tz).replace(microsecond=0)
            api_recent_url = "/".join([current_app.config["API_ENTRYPOINT"], "recent"])
            r = requests.get(api_recent_url, headers=headers)
            most_recent = r.json()["time_last"]

            stats = {
                "current_time": now,
                "most_recent": datetime.fromtimestamp(most_recent, tz=timezone.utc).astimezone(w_tz).replace(microsecond=0)
            }
            current_app.logger.debug("Collected stats: {}".format(stats))
            return render_template("index.html", data=r_j, rdata=rdata, q=q, stats=stats)

    return render_template("index.html")
