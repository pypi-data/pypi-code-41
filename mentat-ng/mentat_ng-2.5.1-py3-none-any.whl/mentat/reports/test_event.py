#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Unit test module for testing the :py:mod:`mentat.reports.event` module.
"""


__author__  = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import os
import unittest
from unittest.mock import Mock, call
import datetime

#
# Custom libraries
#
import mentat.const
import mentat.services.sqlstorage
import mentat.services.eventstorage
import mentat.idea.internal
import mentat.reports.utils
import mentat.reports.event
from mentat.datatype.sqldb import GroupModel, FilterModel, NetworkModel, \
    SettingsReportingModel, EventReportModel

#-------------------------------------------------------------------------------
# NOTE: Sorry for the long lines in this file. They are deliberate, because the
# assertion permutations are (IMHO) more readable this way.
#-------------------------------------------------------------------------------

REPORTS_DIR = '/var/tmp'

class TestMentatReportsEvent(unittest.TestCase):
    """
    Unit test class for testing the :py:mod:`mentat.reports.event` module.
    """

    #
    # Turn on more verbose output, which includes print-out of constructed
    # objects. This will really clutter your console, usable only for test
    # debugging.
    #
    verbose = True

    ideas_raw = [
        {
            'Format': 'IDEA0',
            'ID': 'msg01',
            'DetectTime': '2018-01-01T12:00:00Z',
            'Category': ['Fraud.Phishing'],
            'Description': 'Synthetic example 01',
            'Source': [
                {
                    'IP4': ['192.168.0.2-192.168.0.5', '192.168.0.0/25', '10.0.0.1'],
                    'IP6': ['2001:db8::ff00:42:0/112'],
                    'Proto': ['ssh']
                }
            ],
            'Target': [
                {
                    'IP4': ['10.2.2.0/24'],
                    'IP6': ['2001:ffff::ff00:42:0/112'],
                    'Proto': ['https']
                }
            ],
            'Node': [
                {
                    'Name': 'org.example.kippo_honey',
                    'SW': ['Kippo']
                }
            ],
            '_CESNET' : {
                'ResolvedAbuses' : [
                    'abuse@cesnet.cz'
                ],
                'EventClass' : 'class01',
                'EventSeverity': 'low'
            }
        },
        {
            'Format': 'IDEA0',
            'ID': 'msg02',
            'DetectTime': '2018-01-01T13:00:00Z',
            'Category': ['Recon.Scanning'],
            'Description': 'Synthetic example 02',
            'Source': [
                {
                    'IP4': ['192.168.1.2-192.168.1.5', '192.169.0.0/25', '10.0.0.1'],
                    'IP6': ['2002:db8::ff00:42:0/112']
                }
            ],
            'Target': [
                {
                    'IP4': ['11.2.2.0/24'],
                    'IP6': ['2004:ffff::ff00:42:0/112']
                }
            ],
            'Node': [
                {
                    'Name': 'org.example.dionaea',
                    'SW': ['Dionaea']
                }
            ],
            'Note': 'Test note containing ; CSV delimiter.',
            '_CESNET' : {
                'ResolvedAbuses' : [
                    'abuse@cesnet.cz'
                ],
                'EventClass' : 'anomaly-traffic',
                'EventSeverity': 'low'
            }
        }
    ]

    ideas_obj = list(map(mentat.idea.internal.Idea, ideas_raw))

    def setUp(self):
        """
        Perform test case setup.
        """
        self.sqlstorage = mentat.services.sqlstorage.StorageService(
            url  = 'postgresql://mentat:mentat@localhost/mentat_utest',
            echo = False
        )
        self.sqlstorage.database_drop()
        self.sqlstorage.database_create()

        self.eventstorage = mentat.services.eventstorage.EventStorageService(
            dbname   = 'mentat_utest',
            user     = 'mentat',
            password = 'mentat',
            host     = 'localhost',
            port     = 5432
        )
        self.eventstorage.database_drop()
        self.eventstorage.database_create()
        for event in self.ideas_obj:
            event['_CESNET']['StorageTime'] = datetime.datetime.utcnow()
            self.eventstorage.insert_event(event)

        group = GroupModel(name = 'abuse@cesnet.cz',  source = 'manual', description = 'CESNET, z.s.p.o.')

        FilterModel(group = group, name = 'FLT1', type = 'basic', filter = 'Node.Name == "org.example.kippo_honey"', description = 'DESC1', enabled = True)
        FilterModel(group = group, name = 'FLT2', type = 'basic', filter = 'Category == "Recon.Scanning"', description = 'DESC2', enabled = True)
        NetworkModel(group = group, netname = 'UNET1', source = 'manual', network = '10.0.0.0/8')
        SettingsReportingModel(group = group)

        self.sqlstorage.session.add(group)
        self.sqlstorage.session.commit()

        self.reporting_settings = mentat.reports.utils.ReportingSettings(group)

        self.reporter = mentat.reports.event.EventReporter(
            Mock(),
            REPORTS_DIR,
            os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../conf/templates/reporter')),
            'en',
            'UTC',
            self.eventstorage,
            self.sqlstorage,
            mailer = None
        )

    def tearDown(self):
        self.sqlstorage.session.close()
        self.sqlstorage.database_drop()
        self.eventstorage.database_drop()

    def test_01_csv_dict(self):
        """
        Test :py:func:`mentat.reports.event.csv_dict` function.
        """
        #pprint([mentat.reports.event.csv_dict(x) for x in self.ideas_obj])
        self.assertTrue([mentat.reports.event.csv_dict(x) for x in self.ideas_obj])

    def test_02_save_to_json_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_json_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = 'utest-security-report.json'
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_json_files( # pylint: disable=locally-disabled,protected-access
                self.ideas_obj,
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

        # Test saving file with timestamp information.
        report_file = 'utest-security-report-M20180726SL-HT9TC.json'
        report_path = os.path.join(REPORTS_DIR, '20180726', report_file)

        self.assertEqual(
            self.reporter._save_to_json_files( # pylint: disable=locally-disabled,protected-access
                self.ideas_obj,
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

    def test_03_save_to_csv_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_csv_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = 'utest-security-report.csv'
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_csv_files( # pylint: disable=locally-disabled,protected-access
                self.ideas_obj,
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

        # Test saving file with timestamp information.
        report_file = 'utest-security-report-M20180726SL-HT9TC.csv'
        report_path = os.path.join(REPORTS_DIR, '20180726', report_file)

        self.assertEqual(
            self.reporter._save_to_csv_files( # pylint: disable=locally-disabled,protected-access
                self.ideas_obj,
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

    def test_04_save_to_files(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter._save_to_files` function.
        """
        self.maxDiff = None

        # Test saving file without timestamp information.
        report_file = 'utest-security-report.txt'
        report_path = os.path.join(REPORTS_DIR, report_file)

        self.assertEqual(
            self.reporter._save_to_files( # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT",
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

        # Test saving file with timestamp information.
        report_file = 'utest-security-report-M20180726SL-HT9TC.txt'
        report_path = os.path.join(REPORTS_DIR, '20180726', report_file)

        self.assertEqual(
            self.reporter._save_to_files( # pylint: disable=locally-disabled,protected-access
                "TEST CONTENT",
                report_file
            ),
            (report_path, "{}.zip".format(report_path))
        )
        self.assertTrue(
            os.path.isfile(report_path)
        )
        self.assertTrue(
            os.path.isfile("{}.zip".format(report_path))
        )
        os.unlink(report_path)
        os.unlink("{}.zip".format(report_path))

    def test_05_aggr_events_by_source(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter.aggregate_events_by_source` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()

        reporting_settings = mentat.reports.utils.ReportingSettings(
            abuse_group
        )

        events_aggr = self.reporter.aggregate_events_by_source(self.ideas_obj, reporting_settings)
        self.assertEqual(list(sorted(events_aggr.keys())), ['10.0.0.1'])
        self.assertEqual(list(sorted(map(lambda x: x['ID'], events_aggr['10.0.0.1']))), ['msg01','msg02'])

    def test_06_aggr_events_for_summary(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter.aggregate_events_for_summary` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()

        reporting_settings = mentat.reports.utils.ReportingSettings(
            abuse_group
        )

        events_aggr = self.reporter.aggregate_events_by_source(self.ideas_obj, reporting_settings)
        events_aggr = self.reporter.aggregate_events_for_summary(events_aggr)
        self.assertEqual(list(sorted(events_aggr.keys())), ['anomaly-traffic', 'class01'])
        self.assertEqual(list(sorted(events_aggr['class01'].keys())), ['10.0.0.1'])
        self.assertEqual(list(sorted(events_aggr['anomaly-traffic'].keys())), ['10.0.0.1'])
        self.assertEqual(list(sorted(map(lambda x: x['ID'], events_aggr['class01']['10.0.0.1']))), ['msg01'])

    def test_07_aggr_events_for_extra(self):
        """
        Test :py:func:`mentat.reports.event.EventReporter.aggregate_events_for_extra` function.
        """
        self.maxDiff = None

        events_aggr = self.reporter.aggregate_events_for_extra(self.ideas_obj)
        self.assertEqual(list(sorted(events_aggr.keys())), ['anomaly-traffic', 'class01'])
        self.assertEqual(list(sorted(map(lambda x: x['ID'], events_aggr['class01']))), ['msg01'])
        self.assertEqual(list(sorted(map(lambda x: x['ID'], events_aggr['anomaly-traffic']))), ['msg02'])

    def test_08_filter_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.filter_events` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()

        reporting_settings = mentat.reports.utils.ReportingSettings(
            abuse_group
        )
        events, fltlog = self.reporter.filter_events(self.ideas_obj, abuse_group, reporting_settings)
        self.assertEqual(events, [])
        self.assertEqual(fltlog, {'FLT1': 1, 'FLT2': 1})
        self.reporter.logger.assert_has_calls([
            call.debug("Event matched filtering rule '%s'", 'FLT1'),
            call.debug("Event matched filtering rule '%s'", 'FLT2'),
            call.info('%s: Filters blocked all %d events, nothing to report.', 'abuse@cesnet.cz', 2)
        ])
        self.sqlstorage.session.commit()

        events, fltlog = self.reporter.filter_events(self.ideas_obj, abuse_group, reporting_settings)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == 'FLT1').one()
        self.assertEqual(flt1.hits, 2)

        events, fltlog = self.reporter.filter_events(self.ideas_obj, abuse_group, reporting_settings)
        events, fltlog = self.reporter.filter_events(self.ideas_obj, abuse_group, reporting_settings)
        self.sqlstorage.session.commit()
        flt1 = self.sqlstorage.session.query(FilterModel).filter(FilterModel.name == 'FLT1').one()
        self.assertEqual(flt1.hits, 4)

    def test_09_fetch_severity_events(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.fetch_severity_events` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()

        events = self.reporter.fetch_severity_events(
            abuse_group,
            'low',
            datetime.datetime.utcnow() - datetime.timedelta(seconds = 7200),
            datetime.datetime.utcnow() + datetime.timedelta(seconds = 7200)
        )
        self.assertEqual(list(map(lambda x: x['ID'], events)), ['msg01', 'msg02'])

        events = self.reporter.fetch_severity_events(
            abuse_group,
            'medium',
            datetime.datetime.utcnow() - datetime.timedelta(seconds = 7200),
            datetime.datetime.utcnow() + datetime.timedelta(seconds = 7200)
        )
        self.assertEqual(list(map(lambda x: x['ID'], events)), [])

        events = self.reporter.fetch_severity_events(
            abuse_group,
            'low',
            datetime.datetime.utcnow() - datetime.timedelta(seconds = 7200),
            datetime.datetime.utcnow() - datetime.timedelta(seconds = 3600)
        )
        self.assertEqual(list(map(lambda x: x['ID'], events)), [])

    def test_10_j2t_idea_path_valueset(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.j2t_idea_path_valueset` function.
        """
        self.maxDiff = None

        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj[0], 'Source.Proto'),
            ['ssh']
        )
        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj[0], ['Source.Proto', 'Target.Proto']),
            ['https', 'ssh']
        )

        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj[1], 'Source.Proto'),
            []
        )
        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj[1], ['Source.Proto', 'Target.Proto']),
            []
        )

        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj, 'Source.Proto'),
            ['ssh']
        )
        self.assertEqual(
            self.reporter.j2t_idea_path_valueset(self.ideas_obj, ['Source.Proto', 'Target.Proto']),
            ['https', 'ssh']
        )


    def test_11_render_report_summary(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_summary` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()
        settings = mentat.reports.utils.ReportingSettings(
            abuse_group
        )

        report_txt = self.reporter.render_report_summary(
            self._generate_mock_report(
                self.ideas_obj,
                abuse_group,
                'low',
                mentat.const.REPORTING_MODE_SUMMARY
            ),
            {
                'regular_aggr': self.reporter.aggregate_events_by_source(self.ideas_obj, settings),
                'relapsed_aggr': self.reporter.aggregate_events_by_source(self.ideas_obj, settings)
            },
            self.reporting_settings,
            {"report_access_url": "https://URL/view=", "contact_email": "EMAIL1", "admin_email": "EMAIL2"},
            ["file1.json"]
        )
        print("\n---\nSUMMARY REPORT IN EN:\n---\n")
        print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split('\n')[0], 'Dear colleagues.')

        self.reporting_settings.locale = 'cs'
        self.reporting_settings.timezone = 'Europe/Prague'

        report_txt = self.reporter.render_report_summary(
            self._generate_mock_report(
                self.ideas_obj,
                abuse_group,
                'low',
                mentat.const.REPORTING_MODE_SUMMARY
            ),
            {
                'regular_aggr': self.reporter.aggregate_events_by_source(self.ideas_obj, settings),
                'relapsed_aggr': self.reporter.aggregate_events_by_source(self.ideas_obj, settings)
            },
            self.reporting_settings,
            {"report_access_url": "https://URL/view=", "contact_email": "EMAIL1", "admin_email": "EMAIL2"},
            ["file1.json"]
        )
        print("\n---\nSUMMARY REPORT IN CS:\n---\n")
        print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split('\n')[0], 'Vážení kolegové.')

    def test_12_render_report_extra(self):
        """
        Test :py:class:`mentat.reports.event.EventReporter.render_report_extra` function.
        """
        self.maxDiff = None

        abuse_group = self.sqlstorage.session.query(GroupModel).filter(GroupModel.name == 'abuse@cesnet.cz').one()
        self.sqlstorage.session.commit()

        report_txt = self.reporter.render_report_extra(
            self._generate_mock_report(
                self.ideas_obj,
                abuse_group,
                'low',
                mentat.const.REPORTING_MODE_EXTRA
            ),
            '192.168.1.1',
            self.ideas_obj,
            self.ideas_obj,
            self.reporting_settings,
            {"report_access_url": "https://URL/view=", "contact_email": "EMAIL1", "admin_email": "EMAIL2"},
            ["file1.json"]
        )
        print("\n---\nEXTRA REPORT IN EN:\n---\n")
        print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split('\n')[0], 'Dear colleagues.')

        self.reporting_settings.locale = 'cs'
        self.reporting_settings.timezone = 'Europe/Prague'

        report_txt = self.reporter.render_report_extra(
            self._generate_mock_report(
                self.ideas_obj,
                abuse_group,
                'low',
                mentat.const.REPORTING_MODE_EXTRA
            ),
            '192.168.1.1',
            self.ideas_obj,
            self.ideas_obj,
            self.reporting_settings,
            {"report_access_url": "https://URL/view=", "contact_email": "EMAIL1", "admin_email": "EMAIL2"},
            ["file1.json"]
        )
        print("\n---\nEXTRA REPORT IN CS:\n---\n")
        print(report_txt)
        self.assertTrue(report_txt)
        self.assertEqual(report_txt.split('\n')[0], 'Vážení kolegové.')


    #---------------------------------------------------------------------------


    @staticmethod
    def _generate_mock_report(events, abuse_group, severity, rtype):
        report = EventReportModel(
            group    = abuse_group,
            severity = severity,
            type     = rtype,
            dt_from  = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
            dt_to    = datetime.datetime.utcnow(),

            evcount_rep     = len(events),
            evcount_all     = len(events),
            evcount_flt     = len(events),
            evcount_flt_blk = 1,
            evcount_thr     = len(events),
            evcount_thr_blk = 0,
            evcount_rlp     = 0,

            filtering = {'FLT01':1}
        )
        report.generate_label()
        report.calculate_delta()

        if rtype == mentat.const.REPORTING_MODE_EXTRA:
            report.parent = EventReportModel(
                group    = abuse_group,
                severity = severity,
                type     = mentat.const.REPORTING_MODE_SUMMARY,
                dt_from  = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600),
                dt_to    = datetime.datetime.utcnow(),

                evcount_rep     = len(events),
                evcount_all     = len(events),
                evcount_flt     = len(events),
                evcount_flt_blk = 1,
                evcount_thr     = len(events),
                evcount_thr_blk = 0,
                evcount_rlp     = 0,

                filtering = {'FLT01':1}
            )
            report.parent.generate_label()
            report.parent.calculate_delta()

        report.statistics = mentat.stats.idea.truncate_evaluations(
            mentat.stats.idea.evaluate_events(events)
        )
        return report


#-------------------------------------------------------------------------------


if __name__ == '__main__':
    unittest.main()
