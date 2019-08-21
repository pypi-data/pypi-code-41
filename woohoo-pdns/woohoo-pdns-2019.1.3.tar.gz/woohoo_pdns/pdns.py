# -*- encoding: utf-8 -*-

import logging
import importlib
import ipaddress
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Table
from sqlalchemy import Integer, CHAR, DateTime, String, Float, Boolean
from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy import desc
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, reconstructor
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, FlushError
from sqlalchemy.ext.declarative import declarative_base
from collections import namedtuple

from .util import LoaderCache, sanitise_input, record_to_nt

# declarative_base is a required SQLAlchemy thingy
Base = declarative_base()


# some exceptions we use to specify what exactly went wrong instead of more generic ones
class InvalidEntry(ValueError):
    """When SQLAlchemy fails to commit a record to the database, this exception is raised.

    The details produced by SQLAlchemy will be included in the exceptions description.
    """
    pass


class MissingEntry(ValueError):
    """When a query does not yield any result, this exception is raised."""
    pass


class Record(Base):
    """
    Database representation of a record in the pDNS system.

    A record can be of any DNS type (A, AAAA, TXT, PTR, ...) and has a "left side" (``rrname``) and a "right side"
    (``rdata``). More information about "left hand side" and "right hand side" is available on the `Farsight`_ website
    for example.

    Attributes:
        first_seen (DateTime): The date and time (incl. timezone) when a record was first seen by this pDNS system.
        last_seen (DateTime): The date and time (incl. timezone) when a record was last seen by this pDNS system (i.e.
            the most recent "sighting").
        rrtype (int): The type of the record (A, AAAA, TXT, ...) according to the `official list of DNS types`_.
        hitcount (int): The number of times this record was "sighted" by this pDNS system.

    .. _Farsight: https://www.farsightsecurity.com/txt-record/2015/03/11/stsauver-rrset-rdata/
    .. _official list of DNS types: https://en.wikipedia.org/wiki/List_of_DNS_record_types
    """

    __tablename__ = "record"  # this is a "hint" to SQLAlchemy to control the created table's name

    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    rrtype = Column(Integer, primary_key=True, nullable=False)
    _rrname = Column(String(270), primary_key=True, nullable=False)
    hitcount = Column(Integer, default=1, nullable=False)
    _rdata = Column(String(300), primary_key=True)

    def __init__(self, **kwargs):
        """The init method is just setting up a logger for the class.

        The kwargs just make it a "cooperative class" according to `super() considered super`_.

        .. _super() considered super: https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        """
        self._l = logging.getLogger(__name__)
        super().__init__(**kwargs)

    @property
    def rrname(self):
        """The "rrname", i.e. the "left hand side" of the record (cf. class attribute documentation).

        Note:
            When setting this property, the value will be sanitized by :func:`woohoo_pdns.util.sanitise_input`; this
            means that a trailing dot will be removed unless the value is just a dot.
        """
        return self._rrname

    @rrname.setter
    def rrname(self, new):
        new = sanitise_input(new)
        self._rrname = new

    @property
    def rdata(self):
        """The "rdata", i.e. the "right hand side" of the record (cf. class attribute documentation)."""
        return self._rdata

    @rdata.setter
    def rdata(self, new):
        new = sanitise_input(new)
        self._rdata = new

    @reconstructor
    def ensure_aware_dt(self):
        """When reconstructing a :class:`Record` from the database, ensure that the datetimes (first_seen and last_seen)
        are "aware" objects (i.e. have a timezone).

        This is mainly an issue when using sqlite (e.g. for testing) as sqlite does not store timezone information. In
        case the timezone information is missing, UTC is assumed and added.
        """
        self._l = logging.getLogger(__name__)
        if not self.first_seen.tzinfo:
            # self._l.warning("Reconstructed naive datetime from database for record.first_seen. "
            #                 "This is only expected in development (sqlite)!")
            self.first_seen = self.first_seen.replace(tzinfo=timezone.utc)
        if not self.last_seen.tzinfo:
            # self._l.warning("Reconstructed naive datetime from database for record.last_seen. "
            #                 "This is only expected in development (sqlite)!")
            self.last_seen = self.last_seen.replace(tzinfo=timezone.utc)

    def update(self, rec):
        """Update a record with (potentially) new information from a different record.

        This means updating (adding) the hitcount as well as updating first_seen and/or last_seen if required.

        Args:
            rec (:class:`Record`): The record to take the new information from.
        """
        self.hitcount += rec.hitcount
        if self.first_seen > rec.first_seen:
            self.first_seen = rec.first_seen
        if self.last_seen < rec.last_seen:
            self.last_seen = rec.last_seen

    def to_dict(self):
        """Convert the record object to a dictionary representation that is suitable for SQLAlchemy bulk operations."""
        return {
            "hitcount": self.hitcount,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "rrtype": self.rrtype,
            "_rrname": self.rrname,
            "_rdata": self.rdata,
        }

    def to_jsonable(self):
        """Convert the record object to a JSON-friendly dictionary representation.

        Note:
            This dict is compatible with the `Passive DNS - Common Output Format`_.

        .. _Passive DNS - Common Output Format: http://tools.ietf.org/html/draft-dulaunoy-dnsop-passive-dns-cof-01
        """
        return {
            "hitcount": self.hitcount,
            "time_first": self.first_seen.timestamp(),
            "time_last": self.last_seen.timestamp(),
            "rrtype": self.rrtype,
            "rrname": self.rrname,
            "rdata": self.rdata,
        }

    def __repr__(self):
        return "Record<{} {} {}>".format(self.rrtype, self.rrname, self.rdata)


class Database(object):
    """
    The Database object is the interface to the database holding pDNS records.

    This object is designed as a context manager, it can be used with ``with``.
    """
    def __init__(self, db_url):
        """
        Initialise the connection to the database.

        Args:
            db_url (string): The URL to the database, e.g.
                ``postgresql+psycopg2://user:password@hostname/database_name``
        """
        self._l = logging.getLogger(__name__)  # this logger will be called 'woohoo_pdns.pdns'

        # create the connection to the database (SQLAlchemy magic)
        self.engine = create_engine(db_url, echo=False)
        self.db = scoped_session(sessionmaker(autoflush=True, bind=self.engine))
        self._l.debug("Database object ({0}) has scoped session object '{1}'".format(id(self), id(self.db)))

        # this creates all the tables in the database if they do not already exist
        Base.metadata.create_all(bind=self.engine)

        self._trace = ["a1638.g1.akamai.net"]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        """
        Close the connection to the database.
        It is important to call this method after you are done. Will be called automagically when used with the
        context manager.
        """
        self.db.remove()
        self.engine.dispose()

    @property
    def records(self):
        """A list of all pDNS records in the database."""
        return self.db.query(Record)\
            .order_by(Record._rrname)\
            .all()

    @property
    def count(self):
        """The total number of pDNS records in the database."""
        return self.db.query(Record)\
            .order_by(Record._rrname)\
            .count()

    @property
    def most_recent(self):
        """The most recent record in the database, i.e. the one with the most recent "last_seen" datetime."""
        return self.db.query(Record)\
            .order_by(desc(Record.last_seen))\
            .first()

    def query(self, q, rdata=False):
        """Issue a query against the database.

        When

        Args:
            q (str): the query, can be an IP address (v4 or v6) or text.
            rdata (bool): text queries look for matches on the "left hand side" (rrname) unless this option is set which
                makes the query search for matches on the "right hand side". Use it for example to search for domains
                that share a common name server (NS record).
                For IP address queries, this is ignored; defaults to False.

        Returns:
            A list of records that matches the query term.

        Throws:
            :class:`MissingEntry` if no match is found for the query.
        """
        result = []
        if not isinstance(q, str):
            try:
                q = q.decode("utf-8")
            except AttributeError:
                # not sure what we have here, but it's not 'string like'
                q = None
        if q:
            q = q.strip()
            try:
                ipaddress.ip_address(q)
                result = self._query_for_ip(q)
            except ValueError:
                # not an IP
                result = self._query_for_name(q.lower(), rdata)
        return result

    def add_record(self, rrtype, rrname, rdata, first_seen=None, last_seen=None, num_hits=1):
        """
        Add a (new) record to the database.

        If a record with that rrtype, rrname, rdata already exists in the database, the hitcount is increased by
        num_hits, first_seen or last_seen are updated if necessary and the existing object is returned. Otherwise a new
        object will be created and returned (with hitcount 1, fist_seen = last_seen = sighted_at (or "now" if sighted_at
        is not provided)).

        Args:
            rrtype (int): the id for the DNS record type (e.g. 1 for A, 28 for AAAA, etc. See
                    https://en.wikipedia.org/wiki/List_of_DNS_record_types)
            rrname (string): the "left hand side" of the record; a trailing dot will be removed
            rdata (string): the "right hand side" of the record; a trailing dot will be removed
            first_seen (datetime): the date and time of the first (oldest) sighting; if omitted and also no last_seen
                    is provided "now" will be used
            last_seen (datetime): the date and time of the most recent sighting; if omitted and also no first_seen is
                    provided "now" will be used
            num_hits (int): the number of times this record was seen (will be added to an existing records hitcount)

        Returns:
            A :class:`Record` object representing this record.
        """
        if (not first_seen) and (not last_seen):
            first_seen = datetime.now(timezone.utc)
            last_seen = datetime.now(timezone.utc)
        elif last_seen:
            # we have a last_seen (and potentially also a first_seen)
            if not first_seen:
                # only last_seen provided, use it for both timestamps
                first_seen = last_seen
        else:
            # only first_seen was provided, use it for both timestamps
            last_seen = first_seen

        log_msg = "Detected naive datetime for record.{when}_seen. Assuming UTC."
        when = None
        if not first_seen.tzinfo:
            when = "first"
            first_seen = first_seen.replace(tzinfo=timezone.utc)
        if not last_seen.tzinfo:
            when = " and ".join([when, "last"])
            last_seen = last_seen.replace(tzinfo=timezone.utc)
        if when:
            self._l.debug(log_msg.format(when))

        new_record = Record(
            rrtype=rrtype,
            _rrname=None,
            _rdata=None,
            first_seen=first_seen,
            last_seen=last_seen,
            hitcount=num_hits
        )
        # using the property to set rrname and rdata to ensure  rrname and rdata are being sanitised
        new_record.rrname = rrname
        new_record.rdata = rdata

        try:
            # self._l.debug("Starting find for {} {}".format(rrname, rdata))
            record = self.find_record(new_record.rrtype, new_record.rrname, rdata=new_record.rdata)

            """
            When using sqlite, SQLAlchemy does not use timezone aware datetimes but naive datetimes in UTC...
            https://stackoverflow.com/a/6991536
            https://stackoverflow.com/a/27596917
            """
            if not record.first_seen.tzinfo:
                self._l.warning("Detected naive datetime for record.first_seen. This is only expected in development!")
                record.first_seen = record.first_seen.replace(tzinfo=timezone.utc)
                record.last_seen = record.last_seen.replace(tzinfo=timezone.utc)

            record.update(new_record)
        except MissingEntry:
            self.db.add(new_record)
            record = new_record

        try:
            self.db.commit()
        except (IntegrityError, FlushError) as e:
            self.db.rollback()
            raise InvalidEntry(*e.args)
        return record

    def find_record(self, rrtype, rrname, rdata=None):
        """
        Search for a record (by type and left hand side, optionally also right hand side).

        Args:
            rrtype (int): The id for the DNS record type (e.g. 1 for A, 28 for AAAA, etc. See
                https://en.wikipedia.org/wiki/List_of_DNS_record_types).
            rrname (string): The "left hand side" of the record.
            rdata (string): The "right hand side" of the record.

        Returns:
            The :class:`Record` object representing the record.

        Raises:
            :class:`NoResultFound` if there is no record that matches the criteria.
        """
        self._l.debug("find_record called: rrype '{}', rrname '{}', rrdata '{}'".format(rrtype, rrname, rdata))
        try:
            if not rdata:
                # self._l.debug("Looking for '{}' '{}'".format(rrtype, rrname))
                record = self.db.query(Record) \
                    .filter(
                        Record.rrtype == rrtype,
                        Record._rrname == rrname
                    ) \
                    .first()
                # .first() returns None if no record is found (not like .one() which raises an exception
                if not record:
                    raise MissingEntry("No such record: {} {}".format(rrtype, rrname))
            else:
                # self._l.debug("Looking for '{} '{}' '{}'".format(rrtype, rrname, rrdata))
                record = self.db.query(Record) \
                    .filter(
                    Record.rrtype == rrtype,
                    Record._rrname == rrname,
                    Record._rdata == rdata,
                    ) \
                    .one()
        except NoResultFound:
            raise MissingEntry("No such record: {} {} {}".format(rrtype, rrname, rdata))
        return record

    def _query_for_name(self, q, rdata):
        """
        Query the "rrname" or the "rdata" in the DB.

        Note:
            This is for string queries only (no IP address queries).

        Args:
            q (str): The search term, can contain "*" as a wildcard.
            rdata (bool): If True and the query is a text query, search the right hand side instead of the left hand
            side.

        Returns:
            A list of :class:`Record` objects for records found (can be empty)
        """
        self._l.debug("Looking for '{}'".format(q))
        if rdata:
            query_for = Record._rdata
        else:
            query_for = Record._rrname
        if "*" in q:
            # assume wildcard query...
            q = q.replace("*", "%")
            records = self.db.query(Record) \
                .filter(
                query_for.like(q)
            ) \
                .order_by(desc(Record.last_seen), desc(Record.hitcount), desc(Record._rrname)).all()
        else:
            # assume exact query...
            records = self.db.query(Record) \
                .filter(
                query_for == q
            ) \
                .order_by(desc(Record.last_seen), desc(Record.hitcount), desc(Record._rrname)).all()

        return records

    def _query_for_ip(self, q):
        """
        Query the "rdata" for an IP address.

        Args:
            q (str): the IP address (as a string) to search for.

        Returns:
            A list of :class:`Record` objects for records found (can be empty)
        """
        self._l.debug("Looking for '{}'".format(q))
        records = self.db.query(Record) \
            .filter(
            Record._rdata == q
        ) \
            .order_by(desc(Record.last_seen), desc(Record.hitcount), desc(Record._rrname)).all()

        return records

    def load(self, source_name, batch_size=10000, cfg=None, data_timezone="UTC", strict=False,
             loader="woohoo_pdns.load.SilkFileImporter"):
        """
        Load data into the database.

        The actual work is done by the class referenced in the "loader" argument.

        Args:
            source_name (str): The directory or filename or other reference to the source (e.g. a Kafka topic name)
                where data should be loaded from.
            batch_size (int): For more efficient loading into the database, records are inserted/updated in batches;
                this defines the maximum number of records to process at once.
            cfg (dict): A dictionary with config items that will be passed to the constructor of the :class:`Importer`.
            strict (bool): If true, abort loading if "errors" are detected in the input. If false, try to "fix" the
                error(s) and/or to continue loading remaining data. Default is `False`.
            data_timezone (timezone string): If source data without a timezone specification is found, assume the
                timezone is this.
            loader (:class:`Importer`): Defines what class is used for the actual loading of data.
        """
        max_fail = max([int(batch_size/100), 1])
        module_name, class_name = loader.rsplit(".", 1)
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        importer = cls(source_name, cfg=cfg, data_timezone=data_timezone, strict=strict)
        self._l.info("Using importer class '{}'".format(type(importer)))
        cache = LoaderCache()
        while importer.has_more_data:
            entries_batch = importer.load_batch(batch_size, max_failed_inarow=max_fail)
            for entry in entries_batch.records:
                if entry in cache:
                    cache.add(entry, LoaderCache.MODES.updated)
                else:
                    try:
                        existing_e = self.find_record(entry.rrtype, entry.rrname, entry.rdata)
                        existing_e_nt = record_to_nt(existing_e)
                        cache.add(existing_e_nt, LoaderCache.MODES.cache_only)
                        cache.add(entry, LoaderCache.MODES.updated)
                    except MissingEntry:
                        cache.add(entry, LoaderCache.MODES.new)

            log_msg = "Batch stats: '{}' converted, '{}' loaded and '{}' ignored entries."
            self._l.info(log_msg.format(entries_batch.converted, entries_batch.loaded, entries_batch.ignored))
            self._l.info("Going to INSERT '{}' records".format(len(cache.get_new_entries())))
            self._l.info("Going to UPDATE '{}' records".format(len(cache.get_to_update())))

            self.db.bulk_insert_mappings(Record, cache.get_new_entries(for_bulk=True))
            self.db.bulk_update_mappings(Record, cache.get_to_update(for_bulk=True))
            try:
                self.db.commit()
            except (IntegrityError, FlushError) as e:
                self.db.rollback()
                raise InvalidEntry(*e.args)

            cache.rollover()

            self._l.info("Batch of data loaded, batch size: {}".format(batch_size))
