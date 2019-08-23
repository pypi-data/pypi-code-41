# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for the Rabbit fixture."""

from __future__ import absolute_import, print_function

__metaclass__ = type

import os.path
import socket
import stat
from textwrap import dedent

import amqp
from fixtures import (
    EnvironmentVariableFixture,
    MonkeyPatch,
    TempDir,
    )
from rabbitfixture.server import (
    get_nodename_from_status,
    RabbitServer,
    RabbitServerEnvironment,
    RabbitServerResources,
    )
import six
from testtools import TestCase
from testtools.testcase import gather_details


class TestRabbitFixture(TestCase):

    def setUp(self):
        super(TestRabbitFixture, self).setUp()
        # Rabbit needs to fully isolate itself: an existing per user
        # .erlang.cookie has to be ignored, and ditto bogus HOME if other
        # tests fail to cleanup.
        self.useFixture(EnvironmentVariableFixture('HOME', '/nonsense/value'))

    def test_start_check_shutdown(self):
        # The fixture correctly starts and stops RabbitMQ.
        with RabbitServer() as fixture:
            try:
                # We can connect.
                connect_arguments = {
                    "host": 'localhost:%s' % fixture.config.port,
                    "userid": "guest", "password": "guest",
                    "virtual_host": "/",
                    }
                connection = amqp.Connection(**connect_arguments)
                connection.connect()
                connection.close()
                # And get a log file.
                log = fixture.runner.getDetails()["server.log"]
                # Which shouldn't blow up on iteration.
                list(log.iter_text())
            except Exception:
                # self.useFixture() is not being used because we want to
                # handle the fixture's lifecycle, so we must also be
                # responsible for propagating fixture details.
                gather_details(fixture.getDetails(), self.getDetails())
                raise

        # The daemon should be closed now.
        connection = amqp.Connection(**connect_arguments)
        self.assertRaises(socket.error, connection.connect)

    def test_stop_hang(self):
        # If rabbitctl hangs on shutdown, the fixture eventually manages to
        # stop RabbitMQ anyway.
        bindir = self.useFixture(TempDir()).path
        fakectlbin = os.path.join(bindir, "rabbitmqctl")
        with open(fakectlbin, "w") as f:
            f.write("#! /bin/sh\n")
            f.write("while :; do sleep 1 || exit; done\n")
        os.chmod(fakectlbin, stat.S_IRWXU)

        with RabbitServer(ctltimeout=0.1) as fixture:
            try:
                connect_arguments = {
                    "host": 'localhost:%s' % fixture.config.port,
                    "userid": "guest", "password": "guest",
                    "virtual_host": "/",
                    }

                self.useFixture(MonkeyPatch(
                    "rabbitfixture.server.RabbitServerEnvironment.ctlbin",
                    fakectlbin))
            except Exception:
                # self.useFixture() is not being used because we want to
                # handle the fixture's lifecycle, so we must also be
                # responsible for propagating fixture details.
                gather_details(fixture.getDetails(), self.getDetails())
                raise

        # The daemon should be closed now.
        connection = amqp.Connection(**connect_arguments)
        self.assertRaises(socket.error, connection.connect)

    def test_config(self):
        # The configuration can be passed in.
        config = RabbitServerResources()
        fixture = self.useFixture(RabbitServer(config))
        self.assertIs(config, fixture.config)
        self.assertIs(config, fixture.runner.config)
        self.assertIs(config, fixture.runner.environment.config)

    def test_kill(self):
        # The fixture can kill RabbitMQ even before cleanUp time, if requested.
        with RabbitServer() as fixture:
            fixture.runner.kill()
            # The daemon should be died, even if we didn't run
            # cleanUp yet.
            self.assertFalse(fixture.runner.is_running())


class TestRabbitServerResources(TestCase):

    def test_defaults(self):
        with RabbitServerResources() as resources:
            self.assertEqual("localhost", resources.hostname)
            self.assertIsInstance(resources.port, int)
            self.assertIsInstance(resources.dist_port, int)
            self.assertIsInstance(resources.homedir, six.string_types)
            self.assertIsInstance(resources.mnesiadir, six.string_types)
            self.assertIsInstance(resources.logfile, six.string_types)
            self.assertIsInstance(resources.nodename, six.string_types)
            with open(resources.pluginsfile) as pluginsfile:
                self.assertEqual("[].\n", pluginsfile.read())

    def test_passed_to_init(self):
        args = dict(
            hostname="hostname", port=1234, dist_port=2345,
            homedir="homedir", mnesiadir="mnesiadir",
            logfile="logfile", nodename="nodename")
        resources = RabbitServerResources(**args)
        for i in range(2):
            with resources:
                for key, value in args.items():
                    self.assertEqual(value, getattr(resources, key))

    def test_defaults_reallocated_after_teardown(self):
        seen_homedirs = set()
        resources = RabbitServerResources()
        for i in range(2):
            with resources:
                self.assertTrue(os.path.exists(resources.homedir))
                self.assertNotIn(resources.homedir, seen_homedirs)
                seen_homedirs.add(resources.homedir)

    def test_fq_nodename(self):
        resources = self.useFixture(RabbitServerResources(
            nodename="nibbles", hostname="127.0.0.1"))
        self.assertEqual("nibbles@127.0.0.1", resources.fq_nodename)


class TestRabbitServerEnvironment(TestCase):

    def test_setup(self):
        config = self.useFixture(RabbitServerResources(
            hostname="localhost", port=1234, homedir="rabbit/homedir",
            mnesiadir="rabbit/mnesiadir", logfile="rabbit/logfile",
            nodename="rabbit-nodename"))
        self.useFixture(RabbitServerEnvironment(config))
        expected = {
            "RABBITMQ_MNESIA_BASE": config.mnesiadir,
            "RABBITMQ_LOG_BASE": config.homedir,
            "RABBITMQ_NODE_IP_ADDRESS": socket.gethostbyname(config.hostname),
            "RABBITMQ_NODE_PORT": str(config.port),
            "RABBITMQ_DIST_PORT": str(config.dist_port),
            "RABBITMQ_NODENAME": config.fq_nodename,
            "RABBITMQ_ENABLED_PLUGINS_FILE": config.pluginsfile,
        }
        self.assertEqual(
            expected, {name: os.getenv(name) for name in expected})


class TestFunctions(TestCase):

    def test_get_nodename_from_status(self):
        example_status = dedent("""\
        Status of node tmpTAIyVi@obidos ...
        [{running_applications,
             [{rabbit_management,"RabbitMQ Management Console","0.0.0"},
              {webmachine,"webmachine","1.8.1"},
              {crypto,"CRYPTO version 1","1.6.3"},
              {amqp_client,"RabbitMQ AMQP Client","2.3.1"},
              {rabbit_management_agent,"RabbitMQ Management Agent","0.0.0"},
              {rabbit,"RabbitMQ","2.3.1"},
              {mnesia,"MNESIA  CXC 138 12","4.4.12"},
              {os_mon,"CPO  CXC 138 46","2.2.4"},
              {sasl,"SASL  CXC 138 11","2.1.8"},
              {rabbit_mochiweb,"RabbitMQ Mochiweb Embedding","0.0.0"},
              {stdlib,"ERTS  CXC 138 10","1.16.4"},
              {kernel,"ERTS  CXC 138 10","2.13.4"}]},
         {nodes,[{disc,[tmpTAIyVi@obidos]}]},
         {running_nodes,[tmpTAIyVi@obidos]}]
        """)
        self.assertEqual(
            "tmpTAIyVi@obidos",
            get_nodename_from_status(example_status))

    def test_get_nodename_from_status_no_ellipsis(self):
        # The trailing ellipsis was removed in rabbitmq-server 3.6.10.
        example_status = dedent("""\
        Status of node tmpTAIyVi@obidos
        [{running_applications,
             [{rabbit_management,"RabbitMQ Management Console","0.0.0"},
              {webmachine,"webmachine","1.8.1"},
              {crypto,"CRYPTO version 1","1.6.3"},
              {amqp_client,"RabbitMQ AMQP Client","2.3.1"},
              {rabbit_management_agent,"RabbitMQ Management Agent","0.0.0"},
              {rabbit,"RabbitMQ","2.3.1"},
              {mnesia,"MNESIA  CXC 138 12","4.4.12"},
              {os_mon,"CPO  CXC 138 46","2.2.4"},
              {sasl,"SASL  CXC 138 11","2.1.8"},
              {rabbit_mochiweb,"RabbitMQ Mochiweb Embedding","0.0.0"},
              {stdlib,"ERTS  CXC 138 10","1.16.4"},
              {kernel,"ERTS  CXC 138 10","2.13.4"}]},
         {nodes,[{disc,[tmpTAIyVi@obidos]}]},
         {running_nodes,[tmpTAIyVi@obidos]}]
        """)
        self.assertEqual(
            "tmpTAIyVi@obidos",
            get_nodename_from_status(example_status))
