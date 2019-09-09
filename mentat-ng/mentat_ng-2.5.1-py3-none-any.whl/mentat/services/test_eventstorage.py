#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.eventstorage` module.
"""


__author__  = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import time
import json
import difflib
import unittest
import datetime
import pprint

#
# Custom libraries
#
import mentat.idea.internal
import mentat.services.eventstorage


#-------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
#-------------------------------------------------------------------------------


class TestMentatStorage(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.sqlstorage` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = False

    idea_raw_1 = {
        'Format': 'IDEA0',
        'ID': '4390fc3f-c753-4a3e-bc83-1b44f24baf75',
        'CreateTime': '2012-11-03T10:00:02Z',
        'DetectTime': '2012-11-03T10:00:07Z',
        'WinStartTime': '2012-11-03T05:00:00Z',
        'WinEndTime': '2012-11-03T10:00:00Z',
        'EventTime': '2012-11-03T07:36:00Z',
        'CeaseTime': '2012-11-03T09:55:22Z',
        'Category': ['Fraud.Phishing','Test'],
        'Ref': ['cve:CVE-1234-5678'],
        'Confidence': 1.0,
        'Description': 'Synthetic example',
        'Note': 'Synthetic example note',
        'ConnCount': 20,
        'Source': [
            {
                'Type': ['Phishing'],
                'IP4': ['192.168.0.2-192.168.0.5', '192.168.0.0/25'],
                'IP6': ['2001:db8::ff00:42:0/112'],
                'Hostname': ['example.com'],
                'URL': ['http://example.com/cgi-bin/killemall'],
                'Proto': ['tcp', 'http'],
                'AttachHand': ['att1'],
                'Netname': ['ripe:IANA-CBLK-RESERVED1']
            }
        ],
        'Target': [
            {
                'Type': ['Backscatter', 'OriginSpam'],
                'Email': ['innocent@example.com'],
                'Spoofed': True
            },
            {
                'Type': ['CasualIP'],
                'IP4': ['10.2.2.0/24'],
                'IP6': ['2001:ffff::ff00:42:0/112'],
                'Port': [22, 25, 443],
                'Anonymised': True
            }
        ],
        'Attach': [
            {
                'Handle': 'att1',
                'FileName': ['killemall'],
                'Type': ['Malware'],
                'ContentType': 'application/octet-stream',
                'Hash': ['sha1:0c4a38c3569f0cc632e74f4c'],
                'Size': 46,
                'Ref': ['Trojan-Spy:W32/FinSpy.A'],
                'ContentEncoding': 'base64',
                'Content': 'TVpqdXN0a2lkZGluZwo='
            }
        ],
        'Node': [
            {
                'Name': 'org.example.kippo_honey',
                'Realm': 'cesnet.cz',
                'Type': ['Protocol', 'Honeypot'],
                'SW': ['Kippo'],
                'AggrWin': '00:05:00'
            }
        ],
        '_CESNET' : {
            'StorageTime' : '2017-04-05T10:21:39Z',
            'EventTemplate' : 'sserv-012',
            'ResolvedAbuses' : [
                'abuse@cesnet.cz'
            ],
            'Impact' : 'System provides SDDP service and can be misused for massive DDoS attack',
            'EventClass' : 'vulnerable-config-ssdp',
            'EventSeverity': 'low',
            'InspectionErrors': ['Demonstration error - first', 'Demonstration error - second']
        }
    }

    #
    # This second IDEA message verifies, that is it possible to store messages
    # containing null characters.
    #
    idea_raw_2 = {
        "Attach": [
            {
                "data": "root:zlxx.\u0000\nenable\u0000:system\u0000\nshell\u0000:sh\u0000", "datalen": 38
            }
        ],
        "Category": ["Attempt.Login", "Test"],
        "ConnCount": 1,
        "DetectTime": "2018-04-30T08:54:28.550680Z",
        "Format": "IDEA0",
        "ID": "b434c36f-f0e6-4afb-afab-95863486e76f",
        "Node": [
            {
                "Name": "cz.cesnet.hugo.haas_telnetd",
                "SW": ["telnetd"],
                "Type": ["Honeypot", "Connection"]
            }
        ],
        "Note": "telnetd event",
        "Source": [
            {
                "IP4": ["212.111.222.111"],
                "Port": [3246],
                "Proto": ["tcp"]
            }
        ],
        "Target": [
            {
                "Anonymised": True,
                "IP4": ["192.0.0.0"],
                "Port": [23],
                "Proto": ["tcp"]
            }
        ],
        "_CESNET": {
            'StorageTime' : '2017-04-05T10:21:39Z',
            "EventClass": "attempt-login-telnet",
            "EventSeverity": "medium",
            "SourceResolvedASN": [12338],
            "SourceResolvedCountry": ["ES"]
        }
    }

    def test_01_service(self):  # pylint: disable=locally-disabled,no-self-use
        """
        Perform the basic tests of storage service.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = 'mentat_utest',
            user     = 'mentat',
            password = 'mentat',
            host     = 'localhost',
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()
        storage.database_drop()
        storage.close()

    def test_02_service_manager(self):
        """
        Perform the basic tests of storage service manager.
        """
        self.maxDiff = None

        manager = mentat.services.eventstorage.EventStorageServiceManager(
            {
                '__core__database': {
                    'eventstorage': {
                        'dbname':   'mentat_utest',
                        'user':     'mentatttt',
                        'password': 'mentat',
                        'host':     'localhost',
                        'port':     5432
                    }
                }
            },
            {
                '__core__database': {
                    'eventstorage': {
                        'user': 'mentat'
                    }
                }
            }
        )
        storage = manager.service()
        storage.database_drop()
        storage.database_create()
        storage.database_drop()
        storage.close()
        manager.close()

    def test_03_module_service(self):
        """
        Perform the basic tests of module service.
        """
        self.maxDiff = None

        mentat.services.eventstorage.init(
            {
                '__core__database': {
                    'eventstorage': {
                        'dbname':   'mentat_utest',
                        'user':     'mentatttt',
                        'password': 'mentat',
                        'host':     'localhost',
                        'port':     5432
                    }
                }
            },
            {
                '__core__database': {
                    'eventstorage': {
                        'user': 'mentat'
                    }
                }
            }
        )

        manager = mentat.services.eventstorage.manager()
        storage = manager.service()
        storage.database_drop()
        storage.database_create()
        storage.database_drop()
        storage.close()
        manager.close()

    def test_04_crd(self):
        """
        Perform the basic event create,read,delete tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = 'mentat_utest',
            user     = 'mentat',
            password = 'mentat',
            host     = 'localhost',
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        storage.insert_event(idea_into)
        idea_from = storage.fetch_event(idea_into['ID'])

        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new  = json.dumps(idea_from, indent=4, sort_keys=True, default=idea_from.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        idea_from = storage.fetch_event(idea_into['ID'])
        self.assertTrue(idea_from)
        storage.delete_event(idea_into['ID'])
        idea_from = storage.fetch_event(idea_into['ID'])
        self.assertEqual(idea_from, None)

        idea_into = mentat.idea.internal.Idea(self.idea_raw_2)
        storage.insert_event(idea_into)
        idea_from = storage.fetch_event(idea_into['ID'])
        self.assertTrue(idea_from)

        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new  = json.dumps(idea_from, indent=4, sort_keys=True, default=idea_from.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        idea_from = storage.fetch_event(idea_into['ID'])
        self.assertTrue(idea_from)
        storage.delete_event(idea_into['ID'])
        idea_from = storage.fetch_event(idea_into['ID'])
        self.assertEqual(idea_from, None)

        storage.database_drop()
        storage.close()

    def test_05_build_query(self):
        """
        Perform various query building tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )

        tests = [
            (
                {
                    'parameters': {}
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events'
            ),
            (
                {
                    'parameters': {
                        'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7)
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'dt_to': datetime.datetime(2012, 11, 3, 10, 0, 7),
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "detecttime" <= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7),
                        'dt_to': datetime.datetime(2012, 11, 3, 10, 0, 7),
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "detecttime" >= \'2012-11-03T10:00:07\'::timestamp AND "detecttime" <= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'st_from': datetime.datetime(2012, 11, 3, 10, 0, 7),
                        'st_to': datetime.datetime(2012, 11, 3, 10, 0, 7)
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_storagetime" >= \'2012-11-03T10:00:07\'::timestamp AND "cesnet_storagetime" <= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'st_from': datetime.datetime(2012, 11, 3, 10, 0, 7),
                        'st_to': datetime.datetime(2012, 11, 3, 10, 0, 7)
                    },
                    'qtype': 'delete'
                },
                b'DELETE FROM events WHERE "cesnet_storagetime" >= \'2012-11-03T10:00:07\'::timestamp AND "cesnet_storagetime" <= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'st_from': datetime.datetime(2012, 11, 3, 10, 0, 7),
                        'st_to': datetime.datetime(2012, 11, 3, 10, 0, 7)
                    },
                    'qtype': 'count'
                },
                b'SELECT count(id) FROM events WHERE "cesnet_storagetime" >= \'2012-11-03T10:00:07\'::timestamp AND "cesnet_storagetime" <= \'2012-11-03T10:00:07\'::timestamp'
            ),
            (
                {
                    'parameters': {
                        'source_addrs': ['192.168.1.0/24']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("source_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("source_ip"))'
            ),
            (
                {
                    'parameters': {
                        'source_addrs': ['2001::/54']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("source_ip_aggr_ip6" && \'2001::/54\' AND \'2001::/54\' && ANY("source_ip"))'
            ),
            (
                {
                    'parameters': {
                        'source_addrs': ['192.168.1.0/24', '2001::/54']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE (("source_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("source_ip")) OR ("source_ip_aggr_ip6" && \'2001::/54\' AND \'2001::/54\' && ANY("source_ip")))'
            ),
            (
                {
                    'parameters': {
                        'target_addrs': ['192.168.1.0/24']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("target_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("target_ip"))'
            ),
            (
                {
                    'parameters': {
                        'target_addrs': ['2001::/54']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("target_ip_aggr_ip6" && \'2001::/54\' AND \'2001::/54\' && ANY("target_ip"))'
            ),
            (
                {
                    'parameters': {
                        'target_addrs': ['192.168.1.0/24', '2001::/54']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE (("target_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("target_ip")) OR ("target_ip_aggr_ip6" && \'2001::/54\' AND \'2001::/54\' && ANY("target_ip")))'
            ),
            (
                {
                    'parameters': {
                        'host_addrs': ['192.168.1.0/24']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE (("source_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("source_ip")) OR ("target_ip_aggr_ip4" && \'192.168.1.0/24\' AND \'192.168.1.0/24\' && ANY("target_ip")))'
            ),
            (
                {
                    'parameters': {
                        'source_ports': [22,443]
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "source_port" && ARRAY[22,443]'
            ),
            (
                {
                    'parameters': {
                        'target_ports': [22,443]
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "target_port" && ARRAY[22,443]'
            ),
            (
                {
                    'parameters': {
                        'host_ports': [22,443],
                        'source_ports': [22,443]
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("source_port" && ARRAY[22,443] OR "target_port" && ARRAY[22,443])'
            ),
            (
                {
                    'parameters': {
                        'source_types': ['Test','Tag']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "source_type" && ARRAY[\'Test\',\'Tag\']'
            ),
            (
                {
                    'parameters': {
                        'target_types': ['Test','Tag']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "target_type" && ARRAY[\'Test\',\'Tag\']'
            ),
            (
                {
                    'parameters': {
                        'host_types': ['Test','Tag'],
                        'target_types': ['Test','Tag']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE ("source_type" && ARRAY[\'Test\',\'Tag\'] OR "target_type" && ARRAY[\'Test\',\'Tag\'])'
            ),
            (
                {
                    'parameters': {
                        'protocols': ['tcp', 'ssh']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "protocol" && ARRAY[\'tcp\',\'ssh\']'
            ),
            (
                {
                    'parameters': {
                        'protocols': ['tcp', 'ssh'],
                        'not_protocols': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("protocol" && ARRAY[\'tcp\',\'ssh\'])'
            ),
            (
                {
                    'parameters': {
                        'protocols': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "protocol" = \'{}\''
            ),
            (
                {
                    'parameters': {
                        'protocols': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "protocol" != \'{}\''
            ),
            (
                {
                    'parameters': {
                        'categories': ['Test', 'Category']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "category" && ARRAY[\'Test\',\'Category\']'
            ),
            (
                {
                    'parameters': {
                        'categories': ['Test', 'Category'],
                        'not_categories': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("category" && ARRAY[\'Test\',\'Category\'])'
            ),
            (
                {
                    'parameters': {
                        'categories': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "category" = \'{}\''
            ),
            (
                {
                    'parameters': {
                        'categories': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "category" != \'{}\''
            ),
            (
                {
                    'parameters': {
                        'classes': ['test', 'vulnerable-config-ssdp']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_eventclass" = ANY(ARRAY[\'test\',\'vulnerable-config-ssdp\'])'
            ),
            (
                {
                    'parameters': {
                        'classes': ['test', 'vulnerable-config-ssdp'],
                        'not_classes': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("cesnet_eventclass" = ANY(ARRAY[\'test\',\'vulnerable-config-ssdp\']))'
            ),
            (
                {
                    'parameters': {
                        'classes': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE COALESCE("cesnet_eventclass",\'\') = \'\''
            ),
            (
                {
                    'parameters': {
                        'classes': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE COALESCE("cesnet_eventclass",\'\') != \'\''
            ),
            (
                {
                    'parameters': {
                        'severities': ['test', 'low']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_eventseverity" = ANY(ARRAY[\'test\',\'low\'])'
            ),
            (
                {
                    'parameters': {
                        'severities': ['test', 'low'],
                        'not_severities': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("cesnet_eventseverity" = ANY(ARRAY[\'test\',\'low\']))'
            ),
            (
                {
                    'parameters': {
                        'severities': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE COALESCE("cesnet_eventseverity",\'\') = \'\''
            ),
            (
                {
                    'parameters': {
                        'severities': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE COALESCE("cesnet_eventseverity",\'\') != \'\''
            ),
            (
                {
                    'parameters': {
                        'detectors': ['cz.cesnet.kippo', 'cz.cesnet.dionaea']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_name" && ARRAY[\'cz.cesnet.kippo\',\'cz.cesnet.dionaea\']'
            ),
            (
                {
                    'parameters': {
                        'detectors': ['cz.cesnet.kippo','cz.cesnet.dionaea'],
                        'not_detectors': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("node_name" && ARRAY[\'cz.cesnet.kippo\',\'cz.cesnet.dionaea\'])'
            ),
            (
                {
                    'parameters': {
                        'detectors': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_name" = \'{}\''
            ),
            (
                {
                    'parameters': {
                        'detectors': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_name" != \'{}\''
            ),
            (
                {
                    'parameters': {
                        'detector_types': ['Test', 'Tag']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_type" && ARRAY[\'Test\',\'Tag\']'
            ),
            (
                {
                    'parameters': {
                        'detector_types': ['Test', 'Tag'],
                        'not_detector_types': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("node_type" && ARRAY[\'Test\',\'Tag\'])'
            ),
            (
                {
                    'parameters': {
                        'detector_types': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_type" = \'{}\''
            ),
            (
                {
                    'parameters': {
                        'detector_types': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "node_type" != \'{}\''
            ),
            (
                {
                    'parameters': {
                        'groups': ['abuse@cesnet.cz', 'abuse@nic.cz']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_resolvedabuses" && ARRAY[\'abuse@cesnet.cz\',\'abuse@nic.cz\']'
            ),
            (
                {
                    'parameters': {
                        'groups': ['abuse@cesnet.cz', 'abuse@nic.cz'],
                        'not_groups': True
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE NOT ("cesnet_resolvedabuses" && ARRAY[\'abuse@cesnet.cz\',\'abuse@nic.cz\'])'
            ),
            (
                {
                    'parameters': {
                        'groups': ['__EMPTY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_resolvedabuses" = \'{}\''
            ),
            (
                {
                    'parameters': {
                        'groups': ['__ANY__']
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_resolvedabuses" != \'{}\''
            ),
            (
                {
                    'parameters': {
                        'description': 'Test description'
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "description" = \'Test description\''
            ),
            (
                {
                    'parameters': {
                        'limit': 50
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events LIMIT 50'
            ),
            (
                {
                    'parameters': {
                        'limit': 50,
                        'page': 11
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events LIMIT 50 OFFSET 500'
            ),
            (
                {
                    'parameters': {
                        'groups': ['abuse@cesnet.cz', 'abuse@nic.cz'],
                        'limit': 50,
                        'page': 11
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events WHERE "cesnet_resolvedabuses" && ARRAY[\'abuse@cesnet.cz\',\'abuse@nic.cz\'] LIMIT 50 OFFSET 500'
            ),
            (
                {
                    'parameters': {
                        'sortby': 'detecttime.desc'
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events ORDER BY "detecttime" DESC'
            ),
            (
                {
                    'parameters': {
                        'sortby': 'detecttime.asc'
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events ORDER BY "detecttime" ASC'
            ),
            (
                {
                    'parameters': {
                        'sortby': 'storagetime.desc'
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events ORDER BY "cesnet_storagetime" DESC'
            ),
            (
                {
                    'parameters': {
                        'sortby': 'storagetime.asc'
                    }
                },
                b'SELECT "id","detecttime","category","description","source_ip","target_ip","source_ip_aggr_ip4","source_ip_aggr_ip6","target_ip_aggr_ip4","target_ip_aggr_ip6","source_port","target_port","source_type","target_type","protocol","node_name","node_type","cesnet_resolvedabuses","cesnet_storagetime","cesnet_eventclass","cesnet_eventseverity","cesnet_inspectionerrors","event" FROM events ORDER BY "cesnet_storagetime" ASC'
            ),
        ]

        for test in tests:
            query, params = mentat.services.eventstorage.build_query(**test[0])
            self.assertEqual(
                str(storage.mogrify(query, params)).replace(', ', ','),
                str(test[1]).replace(', ', ',')
            )

        storage.database_drop()
        storage.close()

    def test_06_search_events(self):
        """
        Perform various event search tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        storage.insert_event(idea_into)

        orig = json.dumps([idea_into], indent=4, sort_keys=True, default=idea_into.json_default)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7)
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'dt_to': datetime.datetime(2012, 11, 3, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'st_from': datetime.datetime(2017, 4, 5, 10, 10, 0)
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'st_to': datetime.datetime(2017, 4, 5, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_addrs': ['10.2.2.55']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_addrs': ['10.0.0.0/8']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'host_addrs': ['10.0.0.0/8']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_addrs': ['10.25.2.55']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'source_addrs': ['2001:db8::ff00:42:0/112']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'source_addrs': ['2001:db8::0/64']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'host_addrs': ['2001:db8::0/64']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'source_addrs': ['2001:ffff::ffff:42:0/112']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_ports': [22,888]
            }
        )
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'host_ports': [22,888]
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_ports': [888,999]
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_types': ['Test', 'Backscatter']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'target_types': ['Test', 'Tag']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'source_types': ['Test', 'Phishing']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'host_types': ['Test', 'Phishing']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'source_types': ['Test', 'Tag']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'protocols': ['tcp','ipv6']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'protocols': ['udp','ipv8']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'protocols': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'protocols': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'categories': ['Fraud.Phishing']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'categories': ['Test.Heartbeat']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'categories': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'categories': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'classes': ['test', 'vulnerable-config-ssdp']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'classes': ['test', 'class']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'classes': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'classes': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'severitites': ['test', 'low']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'severities': ['test', 'high']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'severitites': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'severities': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detectors': ['org.example.kippo_honey']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detectors': ['org.another.kippo_honey']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detectors': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detectors': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detector_types': ['Honeypot']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detector_types': ['Test','Tag']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detector_types': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'detector_types': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'groups': ['abuse@cesnet.cz']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'groups': ['abuse@nic.cz']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'groups': ['__ANY__']
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'groups': ['__EMPTY__']
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'description': 'Synthetic example'
            }
        )
        self.assertEqual(ideas_count, 1)
        new  = json.dumps(ideas_from, indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'description': 'Bogus description'
            }
        )
        self.assertEqual(ideas_count, 0)
        self.assertFalse(ideas_from)

        # ---

        #storage.database_drop()
        storage.close()

    def test_07_watchdog_events(self):
        """
        Perform event database watchdog tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        self.assertFalse(storage.watchdog_events(5))

        # ---

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        idea_into['_CESNET']['StorageTime'] = datetime.datetime.utcnow()
        storage.insert_event(idea_into)
        self.assertEqual(storage.count_events(), 1)
        time.sleep(1)

        # ---

        self.assertFalse(storage.watchdog_events(1))
        self.assertTrue(storage.watchdog_events(5))
        self.assertTrue(storage.watchdog_events(900))


    def test_08_count_events(self):
        """
        Perform various event count tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        storage.insert_event(idea_into)

        # ---

        ideas_count = storage.count_events(
            {
                'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7)
            }
        )
        self.assertEqual(ideas_count, 1)

        # ---

        ideas_count = storage.count_events(
            {
                'dt_to': datetime.datetime(2012, 11, 3, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)

        # ---

        ideas_count = storage.count_events(
            {
                'st_from': datetime.datetime(2017, 4, 5, 10, 10, 0)
            }
        )
        self.assertEqual(ideas_count, 1)

        # ---

        ideas_count = storage.count_events(
            {
                'st_to': datetime.datetime(2017, 4, 5, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)

    def test_09_delete_events(self):
        """
        Perform various event delete tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events(
            {
                'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7)
            }
        )
        self.assertEqual(ideas_count, 1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events(
            {
                'dt_to': datetime.datetime(2012, 11, 3, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)

        # ---

        ideas_count = storage.delete_events(
            {
                'st_from': datetime.datetime(2017, 4, 5, 10, 10, 0)
            }
        )
        self.assertEqual(ideas_count, 1)

        # ---

        storage.insert_event(idea_into)
        ideas_count = storage.delete_events(
            {
                'st_to': datetime.datetime(2017, 4, 5, 10, 0, 0)
            }
        )
        self.assertEqual(ideas_count, 0)

    def test_10_distinct_values(self):
        """
        Perform various distinct values tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        storage.insert_event(idea_into)

        ideas_count, ideas_from = storage.search_events()
        self.assertEqual(ideas_count, 1)
        orig = json.dumps(idea_into, indent=4, sort_keys=True, default=idea_into.json_default)
        new  = json.dumps(ideas_from[0], indent=4, sort_keys=True, default=idea_into.json_default)
        self.assertEqual(orig, new, "\n".join([l for l in difflib.context_diff(orig.split("\n"), new.split("\n"))]))

        self.assertEqual(
            storage.distinct_values('category'),
            ['Fraud.Phishing','Test']
        )

        self.assertEqual(
            storage.distinct_values('cesnet_eventclass'),
            ['vulnerable-config-ssdp']
        )

        self.assertEqual(
            storage.distinct_values('cesnet_eventseverity'),
            ['low']
        )

    def test_11_thresholding_cache(self):
        """
        Perform various thresholding cache tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        ttltime = datetime.datetime.utcnow()
        reltime = ttltime - datetime.timedelta(seconds = 300)
        thrtime = reltime - datetime.timedelta(seconds = 300)

        storage.threshold_set('ident1', thrtime, reltime, ttltime)
        storage.threshold_set('ident2', thrtime, reltime, ttltime)
        storage.threshold_set('ident3', thrtime, reltime, ttltime)
        self.assertEqual(storage.thresholds_count(), 3)

        storage.threshold_save('msgid1', 'ident3', 'test@domain.org', 'low', reltime + datetime.timedelta(seconds = 5))
        storage.threshold_save('msgid2', 'ident3', 'test@domain.org', 'low', reltime + datetime.timedelta(seconds = 6))
        storage.threshold_save('msgid3', 'ident2', 'test@domain.com', 'low', reltime + datetime.timedelta(seconds = 2))
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertTrue(storage.threshold_check('ident1', ttltime))
        self.assertTrue(storage.threshold_check('ident1', ttltime - datetime.timedelta(seconds = 300)))
        self.assertFalse(storage.threshold_check('ident1', ttltime + datetime.timedelta(seconds = 300)))

        self.assertEqual(storage.thresholds_clean(ttltime), 0)
        self.assertEqual(storage.thresholded_events_clean(), 0)
        self.assertEqual(storage.thresholds_count(), 3)
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertEqual(storage.thresholds_clean(ttltime - datetime.timedelta(seconds = 300)), 0)
        self.assertEqual(storage.thresholded_events_clean(), 0)
        self.assertEqual(storage.thresholds_count(), 3)
        self.assertEqual(storage.thresholded_events_count(), 3)

        self.assertEqual(storage.thresholds_clean(ttltime + datetime.timedelta(seconds = 300)), 3)
        self.assertEqual(storage.thresholds_count(), 0)
        self.assertEqual(storage.thresholded_events_count(), 3)
        self.assertEqual(storage.thresholded_events_clean(), 3)
        self.assertEqual(storage.thresholds_count(), 0)
        self.assertEqual(storage.thresholded_events_count(), 0)

    def test_12_relapse(self):
        """
        Perform various relapse tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        ttltime = datetime.datetime.utcnow()
        reltime = ttltime - datetime.timedelta(seconds = 300)
        thrtime = reltime - datetime.timedelta(seconds = 300)
        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)

        storage.insert_event(idea_into)
        storage.threshold_set('ident1', thrtime, reltime, ttltime)
        storage.threshold_save(
            idea_into['ID'],
            'ident1',
            'test@domain.org',
            'low',
            reltime - datetime.timedelta(seconds = 300)
        )
        relapses = storage.search_relapsed_events('test@domain.org', 'low', ttltime)
        self.assertEqual(len(relapses), 0)
        count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds = 300))
        self.assertEqual(count, 1)
        count = storage.thresholded_events_clean()
        self.assertEqual(count, 1)
        count = storage.delete_events()
        self.assertEqual(count, 1)

        storage.insert_event(idea_into)
        storage.threshold_set('ident1', thrtime, reltime, ttltime)
        storage.threshold_save(
            idea_into['ID'],
            'ident1',
            'test@domain.org',
            'low',
            reltime + datetime.timedelta(seconds = 100)
        )
        relapses = storage.search_relapsed_events('test@domain.org', 'low', ttltime - datetime.timedelta(seconds = 30))
        self.assertEqual(len(relapses), 0)
        relapses = storage.search_relapsed_events('test@domain.org', 'low', ttltime + datetime.timedelta(seconds = 30))
        self.assertEqual(len(relapses), 1)
        count = storage.thresholds_clean(ttltime + datetime.timedelta(seconds = 300))
        self.assertEqual(count, 1)
        count = storage.thresholded_events_clean()
        self.assertEqual(count, 1)
        count = storage.delete_events()
        self.assertEqual(count, 1)

    def test_12_search_event_ghosts(self):
        """
        Perform various event search tests.
        """
        self.maxDiff = None

        storage = mentat.services.eventstorage.EventStorageService(
            dbname   = "mentat_utest",
            user     = "mentat",
            password = "mentat",
            host     = "localhost",
            port     = 5432
        )
        storage.database_drop()
        storage.database_create()

        idea_into = mentat.idea.internal.Idea(self.idea_raw_1)
        storage.insert_event(idea_into)

        # ---

        ideas_count, ideas_from = storage.search_events(
            {
                'dt_from': datetime.datetime(2012, 11, 3, 10, 0, 7)
            },
            event_factory = mentat.services.eventstorage.record_to_idea_ghost
        )
        if self.verbose:
            pprint.pprint(ideas_from)
        self.assertEqual(ideas_count, 1)
        self.assertEqual(idea_into['ID'], ideas_from[0]['ID'])
        self.assertEqual(idea_into['DetectTime'], ideas_from[0]['DetectTime'])
        self.assertEqual(list(idea_into['Category']), list(ideas_from[0]['Category']))


#-------------------------------------------------------------------------------


if __name__ == "__main__":
    unittest.main()
