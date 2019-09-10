#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
KB4IT module. Entry point.

# Author: Tomás Vírseda <tomasvirseda@gmail.com>
# Version: 0.4
# License: GPLv3
# Description: Build a static documentation site based on Asciidoc
#              sources with Semantic Web technologies.
"""

import os
import argparse
from kb4it.core.mod_env import APP, LPATH, GPATH
from kb4it.core.mod_log import get_logger
from kb4it.services.srv_app import Application
from kb4it.services.srv_rdfdb import KB4ITGraph
from kb4it.services.srv_utils import Utils
from kb4it.services.srv_builder import Builder


class KB4IT(object):
    """KB4IT Application class."""

    params = None
    log = None
    source_path = None
    target_path = None
    numdocs = 0
    tmpdir = None

    def __init__(self, params):
        """Missing class docstring (missing-docstring)."""
        self.params = params
        self.setup_logging(params.LOGLEVEL)
        self.setup_services()
        self.get_services()
        self.setup_environment()

    def get_params(self):
        """Missing docstring."""
        return self.params

    def setup_environment(self):
        """Set up KB4IT environment."""
        self.log.debug("Setting up %s environment", APP['shortname'])
        self.log.debug("Global path: %s", GPATH['ROOT'])
        self.log.debug("Local path: %s", LPATH['ROOT'])

        # Create local paths if they do not exist
        for entry in LPATH:
            self.srvutl.create_directory(LPATH[entry])

    def setup_logging(self, severity=None):
        """Set up logging."""
        self.log = get_logger(__class__.__name__, severity.upper())
        self.log.debug("Log level set to: %s", severity.upper())


    def setup_services(self):
        """Set up services."""
        # Declare and register services
        self.services = {}
        try:
            services = {
                'DB': KB4ITGraph(),
                'App': Application(),
                'Utils' :   Utils(),
                'Builder' : Builder(),
            }
            for name in services:
                self.register_service(name, services[name])
        except Exception as error:
            self.log.error(error)
            raise

    def get_services(self):
        """Get services used in this module."""
        self.srvutl = self.get_service('Utils')

    def get_service(self, name):
        """Get or start a registered service."""
        try:
            service = self.services[name]
            logname = service.__class__.__name__
            if not service.is_started():
                service.start(self, logname, name)
            return service
        except KeyError as service:
            self.log.error("Service %s not registered or not found", service)
            raise


    def register_service(self, name, service):
        """Register a new service."""
        try:
            self.services[name] = service
            self.log.debug("Service '%s' registered", name)
        except KeyError as error:
            self.log.error(error)


    def deregister_service(self, name):
        """Deregister a running service."""
        self.services[name].end()
        self.services[name] = None

    def check_parameters(self, params):
        """Check paramaters from command line."""
        self.params = params
        self.source_path = params.SOURCE_PATH

        self.target_path = params.TARGET_PATH
        if self.target_path is None:
            self.target_path = os.path.abspath(os.path.curdir + '/target')
            self.log.debug("\tNo target path provided. Using: %s", self.target_path)

        if not os.path.exists(self.target_path):
            os.makedirs(self.target_path)
            self.log.debug("\tTarget path %s created", self.target_path)

        self.log.info("\tScript directory: %s", GPATH['ROOT'])
        self.log.info("\tResources directory: %s", GPATH['RESOURCES'])
        self.log.info("\tSource directory: %s", self.source_path)
        self.log.info("\tTarget directory: %s", self.target_path)
        self.log.info("\tTemporary directory: %s", self.tmpdir)


    def run(self):
        """Start application."""
        srvapp = self.get_service('App')
        srvapp.run()


    # ~ def stop(self):
        # ~ """
        # ~ Save graph to file before exiting.
        # ~ """
        # ~ rdf = self.graph.serialize()
        # ~ graph_path = self.target_path + SEP + 'kb4it.rdf'
        # ~ with open(graph_path, 'wb') as frdf:
            # ~ frdf.write(rdf)

def main():
    """Execute application."""
    parser = argparse.ArgumentParser(description='KB4IT by Tomás Vírseda')
    parser.add_argument('-sp', '--source-path', dest='SOURCE_PATH',
                        help='Path for Asciidoc source files.',
                        required=True)
    parser.add_argument('-tp', '--target-path', dest='TARGET_PATH',
                        help='Path for output files')
    parser.add_argument('-log', '--log-level', dest='LOGLEVEL',
                        help='Increase output verbosity',
                        action='store', default='INFO')
    parser.add_argument('--version', action='version',
                        version='%s %s' % (APP['shortname'], APP['version']))
    params = parser.parse_args()
    app = KB4IT(params)
    try:
        app.run()
    except Exception:
        raise
