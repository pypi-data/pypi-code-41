#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.services.geoip` module.
"""


__author__  = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import unittest
import subprocess

#
# Custom libraries
#
import mentat.services.geoip


#-------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
#-------------------------------------------------------------------------------


class TestMentatGeoip(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.services.geoip` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = True

    geoip_test_list = [
        [
            '195.113.144.233', {
                'asn': {
                    'asn': 2852,
                    'ip': '195.113.144.233',
                    'org': 'CESNET z.s.p.o.'
                },
                'city': {
                    'accuracy': 100,
                    'cnt_code': 'EU',
                    'cnt_name': 'Europe',
                    'ctr_code': 'CZ',
                    'ctr_name': 'Czechia',
                    'cty_name': None,
                    'ip': '195.113.144.233',
                    'latitude': 50.0848,
                    'longitude': 14.411200000000001,
                    'timezone': 'Europe/Prague'
                },
                'country': {
                    'cnt_code': 'EU',
                    'cnt_name': 'Europe',
                    'ctr_code': 'CZ',
                    'ctr_name': 'Czechia',
                    'ip': '195.113.144.233'
                }
            }
        ]
        #[
        #    '2001:718:1:6::144:233', {
        #        'asn': {
        #            'asn': 2852,
        #            'ip': '2001:718:1:6::144:233',
        #            'org': 'CESNET z.s.p.o.'
        #        },
        #        'city': {
        #            'accuracy': 50,
        #            'cnt_code': 'EU',
        #            'cnt_name': 'Europe',
        #            'ctr_code': 'CZ',
        #            'ctr_name': 'Czechia',
        #            'cty_name': None,
        #            'ip': '2001:718:1:6::144:233',
        #            'latitude': 50.0848,
        #            'longitude': 14.411200000000001,
        #            'timezone': 'Europe/Prague'
        #        },
        #        'country': {
        #            'cnt_code': 'EU',
        #            'cnt_name': 'Europe',
        #            'ctr_code': 'CZ',
        #            'ctr_name': 'Czechia',
        #            'ip': '2001:718:1:6::144:233'
        #        }
        #    }
        #]
    ]

    def setUp(self):
        """
        Perform test case setup.
        """
        if not os.path.isfile('/var/tmp/GeoLite2-ASN.mmdb'):
            subprocess.call([os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../scripts/fetch-geoipdb.sh')), '-t=/var/tmp'])

    def test_01_lookup_asn(self):
        """
        Perform ASN lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(asndb = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-ASN.mmdb')))
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup_asn(test[0]), test[1]['asn'])

    def test_02_lookup_city(self):
        """
        Perform city lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(citydb = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-City.mmdb')))
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup_city(test[0]), test[1]['city'])

    def test_03_lookup_country(self):
        """
        Perform country lookup tests.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(countrydb = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-Country.mmdb')))
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup_country(test[0]), test[1]['country'])

    def test_04_lookup(self):
        """
        Perform full lookup tests with manually configured geoip service.
        """
        self.maxDiff = None

        geoip = mentat.services.geoip.GeoipService(
            asndb     = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-ASN.mmdb')),
            citydb    = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-City.mmdb')),
            countrydb = os.path.abspath(os.path.join(os.path.dirname(__file__), '/var/tmp/GeoLite2-Country.mmdb'))
        )
        geoip.setup()

        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup(test[0]), test[1])

    def test_05_service_manager(self):
        """
        Perform full lookup tests with service obtained by manually configured service manager.
        """
        self.maxDiff = None

        manager = mentat.services.geoip.GeoipServiceManager(
            {
                "__core__services": {
                    "geoip": {
                        "asndb": "/var/opt/opensourcedbs/GeoLite2-ASN.mmdb",
                        "citydb": "/var/opt/opensourcedbs/GeoLite2-City.mmdb",
                        "countrydb": "/var/opt/opensourcedbs/GeoLite2-Country.mmdb"
                    }
                }
            }
        )

        geoip = manager.service()
        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup(test[0]), test[1])

    def test_06_module_service(self):
        """
        Perform full lookup tests with service obtained by module interface.
        """
        self.maxDiff = None

        mentat.services.geoip.init(
            {
                "__core__services": {
                    "geoip": {
                        "asndb": "/var/opt/opensourcedbs/GeoLite2-ASN.mmdb",
                        "citydb": "/var/opt/opensourcedbs/GeoLite2-City.mmdb",
                        "countrydb": "/var/opt/opensourcedbs/GeoLite2-Country.mmdb"
                    }
                }
            }
        )

        geoip = mentat.services.geoip.service()
        for test in self.geoip_test_list:
            self.assertEqual(geoip.lookup(test[0]), test[1])


#-------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
