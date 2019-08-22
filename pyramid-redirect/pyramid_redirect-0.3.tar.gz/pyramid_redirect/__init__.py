# -*- coding: utf-8 -*-

"""
This is a small pyramid extension that allows to add rules for redirecting
the PATH_INFO portion of a requested URL.

Usage example:
    def main(global_config, **settings):
        config = Configurator(settings=settings)
        config.include('pyramid_redirect')
        # add url redirecting rules...
        #   first parameter is a regular expression
        #   second parameter is the target url
        config.add_redirect_rule(r'/favicon.ico', r'/static/favicon.ico')
        config.add_redirect_rule(r'/gallery/(?P<subpath>.*)',
                                r'/root/%(subpath)s')
        #
        # ... rest of configuration
        #
        # return WSGI application instance
        return config.make_wsgi_app()
"""

# This software is distributed under the FreeBSD License.
# See the accompanying file LICENSE for details.
#
# Copyright 2012 Benjamin Hepp

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPMovedPermanently
import logging
import re


__version__ = 0.3


# Add configuration directive
def includeme(config):
    config.add_directive('add_redirect_rule', add_redirect_rule)
    config.add_tween('pyramid_redirect.redirect_tween_factory')


# Configuration directive for adding a redirect rule
def add_redirect_rule(config, pattern, target, permanent=False):
    tpattern = pattern
    if not pattern.startswith(r'^'):
        tpattern = '^' + tpattern
    if not pattern.endswith(r'$'):
        tpattern = tpattern + r'$'
    cpattern = re.compile(tpattern)
    if not hasattr(config.registry, 'redirect_rules'):
        config.registry.redirect_rules = []
    config.registry.redirect_rules.append((pattern, cpattern, target, permanent))

# Tween to perform URL redirecting before a request is handled by Pyramid
def redirect_tween_factory(handler, registry):

    if not hasattr(registry, 'redirect_rules'):
        return handler

    def redirect_tween(request):
        for pattern, cpattern, target, permanent in request.registry.redirect_rules:
            url = request.url
            if request.registry.settings.get('pyramid_redirect.structlog'):
                import structlog
                logger = structlog.getLogger(__name__)
                logger.debug('Matching Pattern', pattern=pattern, url=url)
            else:
                logger = logging.getLogger(__name__)
                logger.debug('Matching pattern "%s" against "%s" ' \
                    % (pattern, url))
            mo = cpattern.match(url)
            if mo is not None:
                url = target % mo.groupdict()
                if request.registry.settings.get('pyramid_redirect.structlog'):
                    import structlog
                    logger = structlog.getLogger(__name__)
                    logger.info('URL Redirected', from_=request.url, to=url)
                else:
                    logger = logging.getLogger(__name__)
                    logger.info('Redirecting url: %s --> %s' \
                        % (request.url, url))
                if permanent:
                    return HTTPMovedPermanently(url)
                else:
                    return HTTPFound(url)
        return handler(request)

    return redirect_tween
