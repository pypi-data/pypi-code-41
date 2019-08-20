# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

import datetime

from flask.views import MethodView
from flask import request, jsonify, g
from werkzeug.exceptions import BadRequest

from odcs.server import app, db, log, conf, version
from odcs.server.errors import NotFound
from odcs.server.models import Compose
from odcs.common.types import (
    COMPOSE_RESULTS, COMPOSE_FLAGS, COMPOSE_STATES, PUNGI_SOURCE_TYPE_NAMES,
    PungiSourceType, MULTILIB_METHODS)
from odcs.server.api_utils import (
    pagination_metadata, filter_composes, validate_json_data,
    raise_if_input_not_allowed)
from odcs.server.auth import requires_role, login_required
from odcs.server.auth import require_scopes

try:
    from odcs.server.celery_tasks import (
        generate_pulp_compose, generate_pungi_compose)
    CELERY_AVAILABLE = True
except ImportError:
    log.exception(
        "Cannot import celery_tasks. The Celery support is turned off.")
    CELERY_AVAILABLE = False


api_v1 = {
    'composes': {
        'url': '/api/1/composes/',
        'options': {
            'defaults': {'id': None},
            'methods': ['GET'],
        }
    },
    'compose': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['GET'],
        }
    },
    'composes_post': {
        'url': '/api/1/composes/',
        'options': {
            'methods': ['POST'],
        }
    },
    'compose_regenerate': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['PATCH'],
        }
    },
    'composes_delete': {
        'url': '/api/1/composes/<int:id>',
        'options': {
            'methods': ['DELETE'],
        }
    },
    'about': {
        'url': '/api/1/about/',
        'options': {
            'methods': ['GET']
        }
    },
}


class ODCSAPI(MethodView):
    def _get_compose_owner(self):
        if conf.auth_backend == "noauth":
            log.warning(
                "Cannot determine the owner of compose, because "
                "'noauth' auth_backend is used.")
            return "unknown"
        else:
            return g.user.username

    def _get_seconds_to_live(self, request_data):
        if "seconds-to-live" in request_data:
            try:
                return min(int(request_data['seconds-to-live']),
                           conf.max_seconds_to_live)
            except ValueError:
                err = 'Invalid seconds-to-live specified in request: %s' % \
                    request_data
                log.error(err)
                raise ValueError(err)
        else:
            return conf.seconds_to_live

    def get(self, id):
        """ Returns ODCS composes.

        If ``id`` is set, only the ODCS compose defined by that ID is
        returned.

        :query string owner: Return only composes owned by this:ref:`owner<owner>`.
        :query number source_type: Return only composes of this :ref:`source type<source_type>`.
        :query string source: Return only composes built from this :ref:`source<source>`.
        :query number state: Return only composes built from this :ref:`state<state>`.
        :query string order_by: Order the composes by the given field. If ``-`` prefix is used,
            the order will be descending. The default value is ``-id``. Available fields are:

            - :ref:`id<id>`
            - :ref:`owner<owner>`
            - :ref:`source_type<source_type>`
            - :ref:`koji_event<koji_event>`
            - :ref:`state<state>`
            - :ref:`time_to_expire<time_to_expire>`
            - :ref:`time_done<time_done>`
            - :ref:`time_removed<time_removed>`

        :statuscode 200: Composes are returned.
        :statuscode 404: Compose not found.
        """
        if id is None:
            p_query = filter_composes(request)

            json_data = {
                'meta': pagination_metadata(p_query, request.args),
                'items': [item.json() for item in p_query.items]
            }

            return jsonify(json_data), 200

        else:
            compose = Compose.query.filter_by(id=id).first()
            if compose:
                return jsonify(compose.json()), 200
            else:
                raise NotFound('No such compose found.')

    @login_required
    @require_scopes('renew-compose')
    @requires_role('allowed_clients')
    def patch(self, id):
        """ Extends the compose expiration time or regenerates expired compose.

        :query number id: :ref:`ID<id>` of the compose to update/regenerate.
        :jsonparam number seconds-to-live: Number of seconds before the compoose expires.

        :statuscode 200: Compose updated and returned.
        :statuscode 401: User is unathorized.
        :statuscode 404: Compose not found.
        """
        if request.data:
            data = request.get_json(force=True)
        else:
            data = {}
        validate_json_data(data)

        seconds_to_live = self._get_seconds_to_live(data)

        old_compose = Compose.query.filter(
            Compose.id == id,
            Compose.state.in_(
                [COMPOSE_STATES["removed"],
                    COMPOSE_STATES["done"],
                    COMPOSE_STATES["failed"]])).first()

        if not old_compose:
            err = "No compose with id %s found" % id
            log.error(err)
            raise NotFound(err)

        raise_if_input_not_allowed(
            source_types=old_compose.source_type, sources=old_compose.source,
            results=old_compose.results, flags=old_compose.flags,
            arches=old_compose.arches)

        has_to_create_a_copy = old_compose.state in (
            COMPOSE_STATES['removed'], COMPOSE_STATES['failed'])
        if has_to_create_a_copy:
            log.info("%r: Going to regenerate the compose", old_compose)
            compose = Compose.create_copy(db.session,
                                          old_compose,
                                          self._get_compose_owner(),
                                          seconds_to_live)
            db.session.add(compose)
            # Flush is needed, because we use `before_commit` SQLAlchemy
            # event to send message and before_commit can be called before
            # flush and therefore the compose ID won't be set.
            db.session.flush()
            db.session.commit()

            if CELERY_AVAILABLE and conf.celery_broker_url:
                if compose.source_type == PungiSourceType.PULP:
                    generate_pulp_compose.delay(compose.id)
                else:
                    generate_pungi_compose.delay(compose.id)

            return jsonify(compose.json()), 200
        else:
            # Otherwise, just extend expiration to make it usable for longer
            # time.
            extend_from = datetime.datetime.utcnow()
            old_compose.extend_expiration(extend_from, seconds_to_live)
            log.info('Extended time_to_expire for compose %r to %s',
                     old_compose, old_compose.time_to_expire)
            # As well as extending those composes that reuse this this compose,
            # and the one this compose reuses.
            reused_compose = old_compose.get_reused_compose()
            if reused_compose:
                reused_compose.extend_expiration(extend_from, seconds_to_live)
            for c in old_compose.get_reusing_composes():
                c.extend_expiration(extend_from, seconds_to_live)
            db.session.commit()
            return jsonify(old_compose.json()), 200

    @login_required
    @require_scopes('new-compose')
    @requires_role('allowed_clients')
    def post(self):
        """ Creates new ODCS compose request.

        :jsonparam number seconds-to-live: Number of seconds before the compoose expires.
        :jsonparam list flags: List of :ref:`compose flags<flags>` defined as strings.
        :jsonparam list arches: List of :ref:`arches<arches>` the compose should be generated for.
        :jsonparam list multilib_arches: List of :ref:`multilib arches<multilib_arches>`.
        :jsonparam string multilib_method: List defining the :ref:`multilib method<multilib_method>`.
        :jsonparam list lookaside_repos: List of :ref:`lookaside_repos<lookaside_repos>`.
        :jsonparam object source: The JSON object defining the source of compose.
        :jsonparam string source["type"]: String defining the :ref:`source type<source_type>`.
        :jsonparam string source["source"]: String defining the :ref:`source<source>`.
        :jsonparam list source["packages"]: List defining the :ref:`packages<packages>`.
        :jsonparam list source["builds"]: List defining the :ref:`builds<builds>`.
        :jsonparam list source["sigkeys"]: List defining the :ref:`sigkeys<sigkeys>`.
        :jsonparam list source["koji_event"]: List defining the :ref:`sigkeys<sigkeys>`.
        :jsonparam list source["modular_koji_tags"]: List defining the :ref:`modular_koji_tags<modular_koji_tags>`.

        :statuscode 200: Compose request created and returned.
        :statuscode 401: Request not in valid format.
        :statuscode 401: User is unathorized.
        """
        data = request.get_json(force=True)
        if not data:
            raise ValueError('No JSON POST data submitted')

        validate_json_data(data)

        seconds_to_live = self._get_seconds_to_live(data)

        source_data = data.get('source', None)
        if not isinstance(source_data, dict):
            err = "Invalid source configuration provided: %s" % str(data)
            log.error(err)
            raise ValueError(err)

        needed_keys = ["type"]
        for key in needed_keys:
            if key not in source_data:
                err = "Missing %s in source configuration, received: %s" % (key, str(source_data))
                log.error(err)
                raise ValueError(err)

        source_type = source_data["type"]
        if source_type not in PUNGI_SOURCE_TYPE_NAMES:
            err = 'Unknown source type "%s"' % source_type
            log.error(err)
            raise ValueError(err)

        source_type = PUNGI_SOURCE_TYPE_NAMES[source_type]

        source = []
        if "source" in source_data:
            # Use list(set()) here to remove duplicate sources.
            source = list(set(source_data["source"].split(" ")))

        if not source and source_type != PungiSourceType.BUILD:
            err = "No source provided for %s" % source_type
            log.error(err)
            raise ValueError(err)

        # Validate `source` based on `source_type`.
        if source_type == PungiSourceType.RAW_CONFIG:
            if len(source) > 1:
                raise ValueError(
                    'Only single source is allowed for "raw_config" '
                    'source_type')

            source_name_hash = source[0].split("#")
            if (len(source_name_hash) != 2 or not source_name_hash[0] or
                    not source_name_hash[1]):
                raise ValueError(
                    'Source must be in "source_name#commit_hash" format for '
                    '"raw_config" source_type.')

            source_name, source_hash = source_name_hash
            if source_name not in conf.raw_config_urls:
                raise ValueError(
                    'Source "%s" does not exist in server configuration.' %
                    source_name)
        elif source_type == PungiSourceType.MODULE:
            for module_str in source:
                nsvc = module_str.split(":")
                if len(nsvc) < 2:
                    raise ValueError(
                        'Module definition must be in "n:s", "n:s:v" or '
                        '"n:s:v:c" format, but got %s' % module_str)
                if nsvc[0] in conf.base_module_names:
                    raise ValueError(
                        "ODCS currently cannot create compose with base "
                        "modules, but %s was requested." % nsvc[0])

        source = ' '.join(source)

        packages = None
        if "packages" in source_data:
            packages = ' '.join(source_data["packages"])

        builds = None
        if "builds" in source_data:
            builds = ' '.join(source_data["builds"])

        sigkeys = ""
        if "sigkeys" in source_data:
            sigkeys = ' '.join(source_data["sigkeys"])
        else:
            sigkeys = ' '.join(conf.sigkeys)

        koji_event = source_data.get('koji_event', None)

        flags = 0
        if "flags" in data:
            for name in data["flags"]:
                if name not in COMPOSE_FLAGS:
                    raise ValueError("Unknown flag %s", name)
                flags |= COMPOSE_FLAGS[name]

        results = COMPOSE_RESULTS["repository"]
        if "results" in data:
            for name in data["results"]:
                if name not in COMPOSE_RESULTS:
                    raise ValueError("Unknown result %s", name)
                results |= COMPOSE_RESULTS[name]

        arches = None
        if "arches" in data:
            arches = ' '.join(data["arches"])
        else:
            arches = " ".join(conf.arches)

        multilib_arches = ""
        if "multilib_arches" in data:
            multilib_arches = " ".join(data["multilib_arches"])

        lookaside_repos = ""
        if "lookaside_repos" in data:
            lookaside_repos = " ".join(data["lookaside_repos"])

        multilib_method = MULTILIB_METHODS["none"]
        if "multilib_method" in data:
            for name in data["multilib_method"]:
                if name not in MULTILIB_METHODS:
                    raise ValueError("Unknown multilib method \"%s\"" % name)
                multilib_method |= MULTILIB_METHODS[name]

        modular_koji_tags = None
        if "modular_koji_tags" in source_data:
            modular_koji_tags = ' '.join(source_data["modular_koji_tags"])

        module_defaults_url = None
        if "module_defaults_url" in source_data:
            module_defaults_url = source_data["module_defaults_url"]

        module_defaults_commit = None
        if "module_defaults_commit" in source_data:
            module_defaults_commit = source_data["module_defaults_commit"]

        module_defaults = None
        # The "^" operator is logical XOR.
        if bool(module_defaults_url) ^ bool(module_defaults_commit):
            raise ValueError(
                'The "module_defaults_url" and "module_defaults_commit" '
                'must be used together.')
        elif module_defaults_url and module_defaults_commit:
            module_defaults = "%s %s" % (module_defaults_url, module_defaults_commit)

        raise_if_input_not_allowed(
            source_types=source_type, sources=source, results=results,
            flags=flags, arches=arches)

        compose = Compose.create(
            db.session, self._get_compose_owner(), source_type, source,
            results, seconds_to_live,
            packages, flags, sigkeys, koji_event, arches,
            multilib_arches=multilib_arches,
            multilib_method=multilib_method,
            builds=builds,
            lookaside_repos=lookaside_repos,
            modular_koji_tags=modular_koji_tags,
            module_defaults_url=module_defaults)
        db.session.add(compose)
        # Flush is needed, because we use `before_commit` SQLAlchemy event to
        # send message and before_commit can be called before flush and
        # therefore the compose ID won't be set.
        db.session.flush()
        db.session.commit()

        if CELERY_AVAILABLE and conf.celery_broker_url:
            if source_type == PungiSourceType.PULP:
                generate_pulp_compose.delay(compose.id)
            else:
                generate_pungi_compose.delay(compose.id)

        return jsonify(compose.json()), 200

    @login_required
    @require_scopes('delete-compose')
    @requires_role('admins')
    def delete(self, id):
        """ Marks compose as expired to be removed later from ODCS storage.
        The compose metadata are still stored in the ODCS database, only the
        composed files stored in ODCS storage are removed.

        :query number id: :ref:`ID<id>` of the compose to delete.

        :statuscode 200: Compose updated and returned.
        :statuscode 400: Compose is not in done or failed :ref:`state<state>`.
        :statuscode 401: User is unathorized.
        :statuscode 404: Compose not found.
        """
        compose = Compose.query.filter_by(id=id).first()
        if compose:
            # can remove compose that is in state of 'done' or 'failed'
            deletable_states = {n: COMPOSE_STATES[n] for n in ['done', 'failed']}
            if compose.state not in deletable_states.values():
                raise BadRequest('Compose (id=%s) can not be removed, its state need to be in %s.' %
                                 (id, deletable_states.keys()))

            # change compose.time_to_expire to now, so backend will
            # delete this compose as it's an expired compose now
            compose.time_to_expire = datetime.datetime.utcnow()
            compose.removed_by = g.user.username
            db.session.add(compose)
            db.session.commit()
            message = ("The delete request for compose (id=%s) has been accepted and will be"
                       " processed by backend later." % compose.id)
            response = jsonify({'status': 202,
                                'message': message})
            response.status_code = 202
            return response
        else:
            raise NotFound('No such compose found.')


class AboutAPI(MethodView):
    def get(self):
        """ Returns information about this ODCS instance in JSON format.

        :resjson string version: The ODCS server version.
        :resjson string auth_backend: The name of authorization backend this
            server is configured with. Can be one of following:

            - ``noauth`` - No authorization is required.
            - ``kerberos`` - Kerberos authorization is required.
            - ``openidc`` - OpenIDC authorization is required.
            - ``kerberos_or_ssl`` - Kerberos or SSL authorization is required.
            - ``ssl`` - SSL authorization is required.
        :statuscode 200: Compose updated and returned.
        """
        json = {'version': version}
        config_items = ['auth_backend']
        for item in config_items:
            config_item = getattr(conf, item)
            # All config items have a default, so if doesn't exist it is
            # an error
            if not config_item:
                raise ValueError(
                    'An invalid config item of "%s" was specified' % item)
            json[item] = config_item
        return jsonify(json), 200


def register_api_v1():
    """ Registers version 1 of ODCS API. """
    composes_view = ODCSAPI.as_view('composes')
    about_view = AboutAPI.as_view('about')
    for key, val in api_v1.items():
        if key.startswith("compose"):
            app.add_url_rule(val['url'],
                             endpoint=key,
                             view_func=composes_view,
                             **val['options'])
        elif key.startswith("about"):
            app.add_url_rule(val['url'],
                             endpoint=key,
                             view_func=about_view,
                             **val['options'])
        else:
            raise ValueError("Unhandled API key: %s." % key)


register_api_v1()
