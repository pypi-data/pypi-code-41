import logging

import coreapi
from zope.cachedescriptors import property as zproperty

from .api_node import ApiNode
from .rest_result_list import RestResultList

log = logging.getLogger(__name__)


class DrfClient:

    def __init__(self, host_url, username, password, schema_url='/api-schema'):
        self._url = "{}{}".format(host_url, schema_url)
        self._username = username
        self._password = password

    @zproperty.CachedProperty
    def _client(self):
        log.debug("Connecting to {}".format(self._url))
        auth = coreapi.auth.BasicAuthentication(username=self._username, password=self._password)
        client = coreapi.Client(auth=auth)
        return client

    @zproperty.CachedProperty
    def _schema(self):
        log.debug("Getting published api schema from server")
        return self._client.get(self._url)

    @zproperty.CachedProperty
    def api(self):
        log.debug("Creating client bindings based on api schema")
        schema = self._schema

        api = ApiNode()
        for app_name, app in schema.items():
            if not hasattr(api, app_name.split('.')[0]):
                api[app_name.split('.')[0]] = ApiNode()
            _api = api[app_name.split('.')[0]]

            for _app_name in app_name.split('.')[1:]:
                if not hasattr(_api, _app_name):
                    _api[_app_name] = ApiNode()
                _api = _api[_app_name]

            for model_name, model in app.items():
                if not hasattr(_api, model_name):
                    _api[model_name] = ApiNode()

                for ops in model.keys():
                    _api[model_name][ops] = self._create_core_api(
                        app_name,
                        model_name,
                        ops
                    )

        return api

    def _create_core_api(self, app, model, ops):

        def _ops(**kwargs):
            if ops == 'list':
                return RestResultList(
                    self._client,
                    self._schema,
                    app,
                    model,
                    ops,
                    params=kwargs
                )
            else:
                return self._client.action(
                    self._schema,
                    [app,
                     model,
                     ops],
                    params=kwargs
                )

        ops_schema = self._schema.get(app).get(model).get(ops)
        _params_help = '\n'.join([
            "param: {param} (required: {required})".format(param=i.name, required=i.required) for i in ops_schema.fields
        ])
        _ops.__doc__ = "{ops} data from {app}.{model}.\nParameters:\n{params}".format(
            ops=ops.capitalize(),
            app=app,
            model=model,
            params=_params_help
        )
        return _ops
