# -*- encoding: utf-8 -*-

from .meta import types

"""
An example test run::

    import logging
    logging.basicConfig(level=logging.DEBUG)

    from woohoo_pdns.pdns import Database
    d = Database('sqlite:///testdb.db')

    r = d.add_record(1, "foo", "bar.")
    d.find_record(1, "foo")
    d.add_record(1, "foo", "bar", num_hits=40)
    d.find_record(1, "foo")
    
    d.query("gmail-imap.l.google.com")
    d.query("2a00:1450:4001:080b::200a")
    d.query("52.23.93.155")
    d.query("meteoswiss-app.ch")
    d.query("*meteoswiss-app.ch")


Or do the whole thing in memory::

    d = Database('sqlite:///:memory:')
    d.load("dns.txt")
"""
