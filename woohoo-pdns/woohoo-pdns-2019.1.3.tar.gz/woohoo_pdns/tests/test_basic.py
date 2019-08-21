# -*- coding: utf-8 -*-

# Run as follows:
# (pdns) ✔ ~/PycharmProjects/woohoo-pdns [develop|●4✚ 3…20]
# 23:42 $ python woohoo_pdns/tests/test_basic.py

import pkg_resources
import unittest
import json
import tempfile
import logging


from datetime import datetime, timezone, timedelta
from argparse import Namespace
from woohoo_pdns import __main__ as woohoo_main
from woohoo_pdns.meta import types
from woohoo_pdns.pdns import Database, MissingEntry
from woohoo_pdns.util import record_data, LoaderCache
from woohoo_pdns.load import WoohooImportError


class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.conn_str = "sqlite:///test.db"

    def test_module_main_function(self):
        cfg = Namespace(
            conn_str=self.conn_str,
            file=pkg_resources.resource_filename(__name__, "dns_one.csv"),
            data_timezone="UTC",
            pattern="*",
            rename=False,
            batch_size=10,
            loader="woohoo_pdns.load.SilkFileImporter",
            query="0.ch.pool.ntp.org",
            rdata=False
        )
        woohoo_main.load_data(cfg)
        woohoo_main.query(cfg)
        woohoo_main.most_recent(cfg)
        cfg.file = "/dev/null"
        woohoo_main.export_data(cfg)

    def test_load_and_read_record_via_api(self):
        r = self.d.add_record(1, "foo", "bar.")
        r_back = self.d.find_record(1, "foo")
        self.assertEqual(r_back.rdata, "bar")
        r = self.d.add_record(1, "foo", "bar.")
        self.d.add_record(1, "foo", "bar", num_hits=40)
        r_back = self.d.find_record(1, "foo")
        self.assertEqual(r_back.hitcount, 42)
        self.assertEqual(self.d.count, 1)

    def test_load_single_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_one.csv")
        self._l.info("Started loading file '{}'".format(in_file))
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        r = self.d.query("0.ch.pool.ntp.org")
        self.assertIsNotNone(r)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].hitcount, 33)
        self.assertEqual(r[0].rdata, "212.25.1.1")
        r = self.d.query("212.25.1.1")
        self.assertIsNotNone(r)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].hitcount, 33)
        self.assertEqual(r[0].rrname, "0.ch.pool.ntp.org")

    def test_double_load_single_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_one.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)

    def test_load_single_line_different_timeformat(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_one_strptime.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)

    def test_load_erroneous_line(self):
        in_file = pkg_resources.resource_filename(__name__, "illegal.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 0)

    def test_load_truncated_line(self):
        in_file = pkg_resources.resource_filename(__name__, "truncated.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 0)

    def test_load_unparseable_line(self):
        in_file = pkg_resources.resource_filename(__name__, "totally_illegal.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 0)

    def test_load_type0_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_type0.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 0)

    def test_load_rdata_end_dot_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_rdata_end_dot.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        self.assertRaises(MissingEntry, self.d.find_record, 1, "0.ch.pool.ntp.org", rdata="212.25.1.1.")
        try:
            r = self.d.find_record(1, "0.ch.pool.ntp.org", rdata="212.25.1.1")
        except MissingEntry:
            self.fail("find_record unexpectedly raised MissingEntry!")
        self.assertIsNotNone(r)

    def test_load_rrname_end_dot_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_rrname_end_dot.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        self.assertRaises(MissingEntry, self.d.find_record, 1, "0.ch.pool.ntp.org.", rdata="212.25.1.1")
        try:
            r = self.d.find_record(1, "0.ch.pool.ntp.org", rdata="212.25.1.1")
        except MissingEntry:
            self.fail("find_record unexpectedly raised MissingEntry!")
        self.assertIsNotNone(r)

    def test_load_rdata_only_dot_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_rdata_only_dot.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        try:
            r = self.d.find_record(1, "0.ch.pool.ntp.org", rdata=".")
        except MissingEntry:
            self.fail("find_record unexpectedly raised MissingEntry!")
        self.assertIsNotNone(r)

    def test_load_rrname_only_dot_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_rrname_only_dot.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 1)
        try:
            r = self.d.find_record(1, ".", rdata="212.25.1.1")
        except MissingEntry:
            self.fail("find_record unexpectedly raised MissingEntry!")
        self.assertIsNotNone(r)

    def test_load_long_line(self):
        in_file = pkg_resources.resource_filename(__name__, "dns_one_long.csv")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        # self.assertRaises(WoohooImportError, self.d.load, in_file, batch_size=100, cfg=load_cfg)
        self.d.load(in_file, batch_size=100, cfg=load_cfg)
        self.assertEqual(len(self.d.records), 0)

    def test_load_dnstap_single(self):
        in_file = pkg_resources.resource_filename(__name__, "dnstap_one.yml")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSTapFileImporter")
        self.assertEqual(len(self.d.records), 1)

    def test_load_dnstap_double(self):
        in_file = pkg_resources.resource_filename(__name__, "dnstap_two.yml")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSTapFileImporter")
        self.assertEqual(len(self.d.records), 2)

    def test_load_dnstap_multi(self):
        in_file = pkg_resources.resource_filename(__name__, "dnstap_multi_answer.yml")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSTapFileImporter")
        self.assertEqual(len(self.d.records), 9)

    def test_load_dnslog_single(self):
        in_file = pkg_resources.resource_filename(__name__, "dnslog_one.json")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSLogFileImporter")
        self.assertEqual(len(self.d.records), 1)
        r_back = self.d.find_record(12, "24.227.156.213.in-addr.arpa", "mx2.mammut.ch")
        # timezone is removed because sqlite (used for tests) cannot store timezone
        self.assertEqual(r_back.first_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 12))
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSLogFileImporter")
        self.assertEqual(len(self.d.records), 1)
        r_back = self.d.find_record(12, "24.227.156.213.in-addr.arpa", "mx2.mammut.ch")
        self.assertEqual(r_back.hitcount, 2)
        self.assertEqual(r_back.first_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 12))
        self.assertEqual(r_back.last_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 12))

    def test_load_dnslog_double(self):
        in_file = pkg_resources.resource_filename(__name__, "dnslog_two.json")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSLogFileImporter")
        self.assertEqual(len(self.d.records), 2)
        r_back = self.d.find_record(12, "24.227.156.213.in-addr.arpa", "mx2.mammut.ch")
        print(r_back.first_seen)
        self.assertEqual(r_back.hitcount, 2)
        # timezone is removed because sqlite (used for tests) cannot store timezone
        self.assertEqual(r_back.first_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 9))
        self.assertEqual(r_back.last_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 11))
        in_file = pkg_resources.resource_filename(__name__, "dnslog_one.json")
        self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.DNSLogFileImporter")
        self.assertEqual(len(self.d.records), 2)
        r_back = self.d.find_record(12, "24.227.156.213.in-addr.arpa", "mx2.mammut.ch")
        print(r_back.first_seen)
        self.assertEqual(r_back.hitcount, 3)
        self.assertEqual(r_back.first_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 9))
        self.assertEqual(r_back.last_seen.replace(tzinfo=None), datetime(2019, 7, 11, 11, 50, 12))

    def test_load_wrong_loader(self):
        in_file = pkg_resources.resource_filename(__name__, "dnstap_multi_answer.yml")
        rename = False
        load_cfg = {
            "rename": rename,
        }
        self.assertRaises(
            WoohooImportError,
            self.d.load,
            in_file,
            batch_size=100,
            cfg=load_cfg,
            loader="woohoo_pdns.load.SilkFileImporter",
        )
        # self.d.load(in_file, batch_size=100, cfg=load_cfg, loader="woohoo_pdns.load.SilkFileImporter")
        self.assertEqual(len(self.d.records), 0)

    def test_loader_cache_add_and_rollover(self):
        cache = LoaderCache()
        # pristine cache should be empty
        self.assertFalse(cache.get_new_entries())
        self.assertFalse(cache.get_to_update())

        # set up some handy datetimes
        now = datetime.now(timezone.utc)
        before = now - timedelta(hours=4)
        then = now + timedelta(hours=6)
        later = then + timedelta(hours=1)

        # dummy data
        first_seen = now
        last_seen = then
        rrtype = types.TXT
        rrname = "test.txt.rec.ord"
        hitcount = 1
        rdata = "5.4.9.8"

        # add a first entry, ensure it is "new" and the only one
        r1 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r1, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 0)
        self.assertEqual(len(cache.get_new_entries()), 1)

        # add a second entry, ensure it is also "new" and that the first one is still present
        first_seen = now
        last_seen = later
        rrtype = types.A
        rrname = "test.a.rec.ord"
        hitcount = 3
        rdata = "5.4.8.7"
        r2 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r2, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 0)
        self.assertEqual(len(cache.get_new_entries()), 2)

        # add a third entry, pretend it is one to "update"
        first_seen = before
        last_seen = then
        rrtype = types.AAAA
        rrname = "test.aaaa.rec.ord"
        hitcount = 5
        rdata = "5.4.7.6"
        r3 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r3, LoaderCache.MODES.updated)
        self.assertEqual(len(cache.get_to_update()), 1)
        self.assertEqual(len(cache.get_new_entries()), 2)

        # assume we consumed all dirty entries and want to start over with a prepopulated cache
        cache.rollover()
        self.assertEqual(len(cache.get_to_update()), 0)
        self.assertEqual(len(cache.get_new_entries()), 0)

        # add the same second entry again, this should update the hitcount
        cache.add(r2, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 1)
        self.assertEqual(len(cache.get_new_entries()), 0)
        update_entries = cache.get_to_update()
        self.assertEqual(update_entries[0].hitcount, 6)
        self.assertEqual((update_entries[0].first_seen - now).total_seconds(), 0)
        self.assertEqual((update_entries[0].last_seen - later).total_seconds(), 0)

        # add a modified first entry again, this should update the hitcount and the first_seen
        first_seen = before
        last_seen = then
        rrtype = types.TXT
        rrname = "test.txt.rec.ord"
        hitcount = 11
        rdata = "5.4.9.8"
        r1_1 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r1_1, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 0)
        update_entries = cache.get_to_update()
        # print(json.dumps(update_entries, indent=4, default=str))
        self.assertEqual(update_entries[1].hitcount, 12)
        self.assertEqual((update_entries[1].first_seen - before).total_seconds(), 0)
        self.assertEqual((update_entries[1].last_seen - then).total_seconds(), 0)

        # add yet another modified first entry, this should update the hitcount and the last_seen
        first_seen = then
        last_seen = later
        rrtype = types.TXT
        rrname = "test.txt.rec.ord"
        hitcount = 13
        rdata = "5.4.9.8"
        r1_2 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r1_2, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 0)
        update_entries = cache.get_to_update()
        # print(json.dumps(update_entries, indent=4, default=str))
        self.assertEqual(update_entries[1].rdata, rdata)
        self.assertEqual(update_entries[1].hitcount, 25)
        self.assertEqual((update_entries[1].first_seen - before).total_seconds(), 0)
        self.assertEqual((update_entries[1].last_seen - later).total_seconds(), 0)

        # add yet another modified first entry, this should only update the hitcount
        first_seen = now
        last_seen = now
        rrtype = types.TXT
        rrname = "test.txt.rec.ord"
        hitcount = 17
        rdata = "5.4.9.8"
        r1_3 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r1_3, LoaderCache.MODES.auto)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 0)
        update_entries = cache.get_to_update()
        # print(json.dumps(update_entries, indent=4, default=str))
        self.assertEqual(update_entries[1].rdata, rdata)
        self.assertEqual(update_entries[1].hitcount, 42)
        self.assertEqual((update_entries[1].first_seen - before).total_seconds(), 0)
        self.assertEqual((update_entries[1].last_seen - later).total_seconds(), 0)

        # add a "new" entry
        first_seen = now
        last_seen = now
        rrtype = types.PTR
        rrname = "test.ptr.rec.ord"
        hitcount = 19
        rdata = "5.4.6.7"
        r4 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r4, LoaderCache.MODES.new)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 1)

        # add another "new" entry
        first_seen = now
        last_seen = later
        rrtype = types.PTR
        rrname = "test.ptr.rec.ord"
        hitcount = 23
        rdata = "5.4.6.7"
        r4_1 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r4_1, LoaderCache.MODES.new)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 1)
        new_entries = cache.get_new_entries()
        # print(json.dumps(update_entries, indent=4, default=str))
        self.assertEqual(new_entries[0].rdata, rdata)
        self.assertEqual(new_entries[0].hitcount, 42)
        self.assertEqual((new_entries[0].first_seen - now).total_seconds(), 0)
        self.assertEqual((new_entries[0].last_seen - later).total_seconds(), 0)

        # add a "cache_only" entry
        first_seen = before
        last_seen = now
        rrtype = types.SOA
        rrname = "test.soa.rec.ord"
        hitcount = 31
        rdata = "5.4.5.6"
        r5 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r5, LoaderCache.MODES.cache_only)
        self.assertEqual(len(cache.get_to_update()), 2)
        self.assertEqual(len(cache.get_new_entries()), 1)

        # add another "cache_only" entry, this should make the entry "move" to the updated entries
        first_seen = now
        last_seen = then
        rrtype = types.SOA
        rrname = "test.soa.rec.ord"
        hitcount = 37
        rdata = "5.4.5.6"
        r5_1 = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        cache.add(r5_1, LoaderCache.MODES.cache_only)
        self.assertEqual(len(cache.get_to_update()), 3)
        self.assertEqual(len(cache.get_new_entries()), 1)
        update_entries = cache.get_to_update()
        # print(json.dumps(update_entries, indent=4, default=str))
        self.assertEqual(update_entries[2].rdata, rdata)
        self.assertEqual(update_entries[2].hitcount, 68)
        self.assertEqual((update_entries[2].first_seen - before).total_seconds(), 0)
        self.assertEqual((update_entries[2].last_seen - then).total_seconds(), 0)

        # clear the cache
        cache.clear()
        self.assertEqual(len(cache.get_to_update()), 0)
        self.assertEqual(len(cache.get_new_entries()), 0)

    def test_meta(self):
        self.assertEqual(repr(types), "<lookup 'DNStypes'>")
        self.assertEqual(types.get("SRV"), 33)
        self.assertIsNone(types.get("FOO"))

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self._l = logging.getLogger(__name__)
        self.db_fp = tempfile.NamedTemporaryFile()
        self.conn_str = "sqlite:///{}".format(self.db_fp.name)
        self._l.info("Testrun is starting...")
        self._l.debug("conn_str: {}".format(self.conn_str))
        self.d = Database(self.conn_str)

    def tearDown(self):
        self._l.info("Deleting test db...")
        del self.d


if __name__ == '__main__':
    unittest.main()