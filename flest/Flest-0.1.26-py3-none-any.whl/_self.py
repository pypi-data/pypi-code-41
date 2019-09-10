# -*- coding: utf-8 -*-
"""
    flest._self
    ~~~~~~~~~~

    main code of Flest.
"""
import sys
import inspect
from importlib import import_module
import flask
from ._utils import _join_paths, _up_in_path
from . config import Config


class Flest(flask.Flask):
    '''Flest - a small contribution to Flask world'''
    config_class = Config

    def _add_rule_for_view(self, prefix, vf, bp):
        url = _join_paths(prefix, vf.__name__)
        if vf.__name__ == 'index':
            url = _join_paths(prefix, '/')

        options = {}
        cl = ['methods', 'defaults', 'host', 'subdomain']
        for k in cl:
            if k in vf.__dict__:
                options[k] = getattr(vf, k)
        if 'methods' not in options:
            options['methods'] = ['GET', 'POST', 'HEAD']

        obj = bp or self
        obj.add_url_rule(
            url,
            _join_paths(
                getattr(
                    sys.modules[vf.__module__],
                    '_blueprint_p',
                    ''
                ),
                vf.__name__,
                delim=':'
            ),
            vf,
            **options
        )

    def mount(self, module, prefix='/'):
        '''mount a module/package'''
        pkg_prefix = prefix = _join_paths(prefix)

        bpr = bp = getattr(module, '_blueprint', None)
        bpnp = getattr(module, '_blueprint_p', '')
        if not bp:
            bp = getattr(module, '_blueprint_i', None)
        if not bp and '__path__' not in module.__dict__:
            p = import_module(_up_in_path(module.__name__))
            if '_blueprint' in p.__dict__:
                bpr = bp = module._blueprint_i = p._blueprint

        for x in dir(module):
            vf = getattr(module, x)
            if(
                inspect.isfunction(vf)
                and vf.__module__.startswith(module.__name__)
                and not x.startswith('_')
            ):
                self._add_rule_for_view(prefix, vf, bp)

        if '_initialize' in module.__dict__:
            module._initialize(self)

        for sub in getattr(module, '_include', []):
            pn = module.__name__
            if '__path__' not in module.__dict__:
                pn = _up_in_path(pn)
            m = import_module('.' + sub, pn)
            if (
                bp
                and '_blueprint' not in m.__dict__
                and '_blueprint_i' not in m.__dict__
            ):
                m._blueprint_i = bp
            m._blueprint_p = _join_paths(bpnp, delim=':')

            self.mount(m, prefix)

        for sub in getattr(module, '_submodules', []):
            m_prefix = _join_paths(prefix, sub)
            m = import_module('.' + sub, module.__name__)
            if (
                bp
                and '_blueprint' not in m.__dict__
                and '_blueprint_i' not in m.__dict__
            ):
                m._blueprint_i = bp
            m._blueprint_p = _join_paths(bpnp, sub, delim=':')

            self.mount(m, m_prefix)

        if bpr:
            url_prefix = getattr(
                bpr, 'url_prefix',
                None # TODO: mystery - _join_paths here doesn't work
            )
            if not url_prefix:
                url_prefix = _join_paths(pkg_prefix, bp.name)
            self.register_blueprint(bpr, url_prefix=url_prefix)

    def preprocess_request(self):
        """Called before the request is dispatched. Calls
        :attr:`url_value_preprocessors` registered with the app and the
        current blueprint (if any). Then calls :attr:`before_request_funcs`
        registered with the app and the blueprint.

        If any :meth:`before_request` handler returns a non-None value, the
        value is handled as if it was the return value from the view, and
        further request handling is stopped.

        .. version changed:: Flest
           prepare function argument for the view function
        """
        req = flask._request_ctx_stack.top.request
        rule = req.url_rule
        if getattr(rule, 'endpoint', None):
            self.view = vf = self.view_functions[rule.endpoint]
            va = {}
            params = req.args.copy()
            params.update(req.form)
            cx = dictobj(
                params=dictobj(params),
                request=req,
                name=vf.__name__,
                json=dictobj(req.json or {}),
                g=flask.g,
                session=flask.session,
                config=self.config,
                flash=flask.flash,
                signin=flask.session.get('signin', None)
            )
            for a in inspect.getfullargspec(vf).args:
                if a in req.view_args:
                    va[a] = req.view_args[a]
                elif a in req.args:
                    va[a] = req.args[a]
                elif a in req.form:
                    va[a] = req.form[a]
                elif a == 'context':
                    va[a] = cx
                elif a in cx:
                    va[a] = cx[a]
                elif a == 'self':
                    pass
                elif a in flask.g:
                    va[a] = getattr(flask.g, a)
                elif a in flask.session:
                    aa = flask.session.get(a)
                    if isinstance(aa, dict):
                        aa = dictobj(aa)
                    va[a] = aa
                elif a in req.__dict__:
                    va[a] = getattr(req, a, None)
                else:
                    #nothing = "@@!! nothing !!@@"
                    nothing = None
                    ra = getattr(req, a, nothing)
                    if ra == nothing:
                        va[a] = ra
                    else:
                        va[a] = ra
            req.view_args = va
        return super().preprocess_request()

    def finalize_request(self, rv, from_error_handler=False):
        """Given the return value from a view function this finalizes
        the request by converting it into a response and invoking the
        postprocessing functions.  This is invoked for both normal
        request dispatching as well as error handlers.

        Because this means that it might be called as a result of a
        failure a special safe mode is available which can be enabled
        with the `from_error_handler` flag.  If enabled, failures in
        response processing will be logged and otherwise ignored.

        :internal:
        """
        te = False
        tname = None
        if isinstance(rv, HTMLResponse):
            tname = rv.template
            rv = rv.rv
            te = True

        if isinstance(rv, JSONResponse):
            rv = flask.jsonify(rv.rv)
        elif isinstance(rv, RedirectResponse) or isinstance(rv, RawResponse):
            rv = rv.rv
        elif isinstance(rv, dict):
            req = flask._request_ctx_stack.top.request
            if not tname:
                vf = self.view_functions[req.url_rule.endpoint]
                tname = vf.__name__
                if tname == 'index':
                    tname = vf.__module__.split('.')[-1]
                tname = getattr(vf, 'template', tname)
            tname += '.html'
            try:
                rv = flask.render_template(tname, **rv)
            except Exception:
                if te:
                    raise

        return super().finalize_request(rv, from_error_handler)


class FlestResponse(object):
    pass


class HTMLResponse(FlestResponse):
    '''HTML response, enforced. Flest will treat the return object as the
    context to be passed to Jinja2 renderer. Exception raised if no template
    file is found to be associated to the view function.
    By default, the returns with no specific Flest response type indication
    will be treated as a "Flexible" response type -- Flest will first search
    for a template associated to the view function (either by function name
    or by the 'template' attribute of the function). If found, the return
    value will be treated as a HTMLResponse but if not found, it will be
    treated as a JSONResponse.
    '''
    def __init__(self, *args, **kwargs):
        self.rv = {}
        self.template = None
        for arg in args:
            if isinstance(arg, dict):
                self.rv.update(arg)
            if isinstance(arg, str):
                self.template = arg
        if kwargs:
            self.rv.update(kwargs)

    def render(self, *args, **kwargs):
        if not self.template:
            raise Exception('No template name')

        cx = self.rv.copy()
        for aa in args:
            if isinstance(aa, dict):
                cx.update(aa)
        cx.update(kwargs)
        return flask.render_template(self.template + '.html', **cx)


class JSONResponse(FlestResponse):
    '''JSON response, enforced. Flest will treat the return value/object as
    JSON response, without looking for an associated template.
    '''
    def __init__(self, *args, **kwargs):
        if kwargs:
            self.rv = {}
            if args and (len(args) > 1 or not isinstance(args[0], dict)):
                raise Exception(
                    'Upto one dict type positional arg allowed '
                    'when **kwargs is provided'
                )
            if args:
                self.rv = args[0]
            self.rv.update(kwargs)
        elif args:
            if isinstance(args[0], dict):
                self.rv = {}
                for arg in args:
                    self.rv.update(arg)
            elif len(args) == 1:
                if isinstance(args[0], JSONResponse):
                    self.rv = args[0].rv
                else:
                    self.rv = args[0]
            else:
                self.rv = args
        else:
            self.rv = None

    def __setitem__(self, key, val):
        if not self.rv:
            self.rv = {}
        if isinstance(self.rv, dict):
            self.rv[key] = val
        else:
            raise TypeError

    def __getitem__(self, key):
        if isinstance(self.rv, dict):
            return self.rv[key]
        else:
            raise TypeError


class RawResponse(FlestResponse):
    def __init__(self, obj):
        self.rv = obj


class RedirectResponse(FlestResponse):
    def __init__(self, target):
        try:
            target = flask.url_for(target)
        except Exception:
            pass

        self.rv = flask.redirect(target)


class dictobj(dict):
    def __init__(self, *args, **kwargs):
        self.__dict__['_nil_'] = False
        if len(args) > 0:
            if args[0] is None:
                args = []
            elif args[0] == 'nil':
                self.__dict__['_nil_'] = True
                return
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if self._nil_:
            return self
        x = super().get(key, None)
        if isinstance(x, dictobj) or isinstance(x, Config):
            pass
        elif isinstance(x, dict):
            x = dictobj(x)

        if key not in self:
            x = dictobj('nil')

        return x

    __getattr__ = __getitem__

    def __setattr__(self, key, value):
        self[key] = value


def declare_blueprint(name, **kwargs):
    '''Create a blueprint at the path wherein the calling function resides.
    '''
    pname = __name__

    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    pname = mod.__name__
    if '__path__' not in mod.__dict__:
        pname = _up_in_path(mod.__name__)
    p = import_module(pname)
    if '_blueprint' in p.__dict__:
        raise Exception('Blueprint already declared')
    bpo = dict(
        template_folder='templates',
        static_folder='static',
    )
    bpo.update(kwargs)
    prefix = bpo.pop('url_prefix', None)
    p._blueprint = flask.Blueprint(name, pname, **bpo)
    if prefix:
        p._blueprint.url_prefix = prefix
