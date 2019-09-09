#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
Event database storage abstraction layer. The current implementation requires
the `PostgreSQL <https://www.postgresql.org/>`__ database and is based directly
on the `Psycopg2 <http://initd.org/psycopg/docs/>`__ library for performance reasons.

.. warning::

    Current implementation is for optimalization purposes using some advanced
    schema features provided by the `PostgreSQL <https://www.postgresql.org/>`__
    database and thus no other engines are currently supported.

.. warning::

    The PostgreSQL extension `ip4r <https://github.com/RhodiumToad/ip4r>`__ must be installed.

References
^^^^^^^^^^

* https://github.com/RhodiumToad/ip4r
* https://www.gab.lc/articles/manage_ip_postgresql_with_ip4r
* http://initd.org/psycopg/docs/usage.html
* http://initd.org/psycopg/docs/sql.html
* http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax


"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Radko Krkoš <radko.krkos@cesnet.cz>, Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import copy
import psycopg2
import psycopg2.extras
import psycopg2.sql

#
# Custom libraries
#
import ipranges
import mentat.idea.sqldb
import mentat.idea.internal
from mentat.const import CKEY_CORE_DATABASE, CKEY_CORE_DATABASE_EVENTSTORAGE


_MANAGER = None

QTYPE_SELECT = 'select'
QTYPE_COUNT  = 'count'
QTYPE_DELETE = 'delete'

ENUM_TABLES = (
    "category",
    "protocol",
    "node_name",
    "node_type",
    "source_type",
    "target_type",
    "cesnet_resolvedabuses",
    "cesnet_eventclass",
    "cesnet_eventseverity",
    "cesnet_inspectionerrors"
)

EVENT_COLUMNS = (
    "id",
    "detecttime",
    "category",
    "description",
    "source_ip",
    "target_ip",
    "source_ip_aggr_ip4",
    "source_ip_aggr_ip6",
    "target_ip_aggr_ip4",
    "target_ip_aggr_ip6",
    "source_port",
    "target_port",
    "source_type",
    "target_type",
    "protocol",
    "node_name",
    "node_type",
    "cesnet_resolvedabuses",
    "cesnet_storagetime",
    "cesnet_eventclass",
    "cesnet_eventseverity",
    "cesnet_inspectionerrors",
    "event"
)

class EventStorageException(Exception):
    """
    Class for custom event storage exceptions.
    """


class StorageIntegrityError(EventStorageException):
    """
    Class for custom event storage exceptions related to integrity errors.
    """


class StorageConnectionException(EventStorageException):
    """
    Class for custom event storage exceptions related to database connection errors.
    """


class DataError(EventStorageException):
    """
    Class for custom event storage exceptions related to data errors.
    """


def _bq_param_multi_to_array(chunks, params, identifier, parameter, negate = False):
    """
    SQL query builder helper. Build part of the query for multi to array parameter.
    """
    if '__EMPTY__' in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL('{} = \'{{}}\'').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT ({} = \'{{}}\')').format(psycopg2.sql.Identifier(identifier)))
    elif '__ANY__' in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL('{} != \'{{}}\'').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT ({} != \'{{}}\')').format(psycopg2.sql.Identifier(identifier)))
    else:
        if not negate:
            chunks.append(psycopg2.sql.SQL('{} && %s').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT ({} && %s)').format(psycopg2.sql.Identifier(identifier)))
        params.append(parameter)


def _bq_param_multi_to_scalar(chunks, params, identifier, parameter, negate = False):
    """
    SQL query builder helper. Build part of the query for multi to scalar parameter.
    """
    if '__EMPTY__' in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL('COALESCE({},\'\') = \'\'').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT (COALESCE({},\'\') = \'\')').format(psycopg2.sql.Identifier(identifier)))
    elif '__ANY__' in parameter:
        if not negate:
            chunks.append(psycopg2.sql.SQL('COALESCE({},\'\') != \'\'').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT (COALESCE({},\'\') != \'\')').format(psycopg2.sql.Identifier(identifier)))
    else:
        if not negate:
            chunks.append(psycopg2.sql.SQL('{} = ANY(%s)').format(psycopg2.sql.Identifier(identifier)))
        else:
            chunks.append(psycopg2.sql.SQL('NOT ({} = ANY(%s))').format(psycopg2.sql.Identifier(identifier)))
        params.append(parameter)

def _bq_gen_aggr_ident(ident, value):
    if ':' in str(value):
        return '{}_aggr_ip6'.format(ident)
    return '{}_aggr_ip4'.format(ident)

def _bq_searchby_addr(chunks, params, idents, items):
    items_exp = []
    chunks.append(
        psycopg2.sql.SQL('({})' if len(items) > 1 or len(idents) > 1 else '{}').format(
            psycopg2.sql.SQL(' OR ').join(
                [
                    psycopg2.sql.SQL('({} && %s AND %s && ANY({}))').format(
                        psycopg2.sql.Identifier(_bq_gen_aggr_ident(ident, itm)),
                        psycopg2.sql.Identifier(ident)
                    ) for ident in idents for itm in items
                ]
            )
        )
    )
    for ident in idents:
        for i in items:
            items_exp.append(i)
            items_exp.append(i)
    params.extend(items_exp)

def build_query(parameters = None, qtype = QTYPE_SELECT, columns = EVENT_COLUMNS):  # pylint: disable=locally-disabled,too-many-branches
    """
    Build SQL database query according to given parameters.

    :param dict parameters: Query parametersas complex dictionary structure.
    :param str qtype: Type of the generated query ('select','count','delete').
    :return: Generated query as ``psycopg2.sql.SQL`` and apropriate arguments.
    :rtype: tuple
    """
    chunks = []
    params = []
    query  = None

    # Prepare query base.
    if qtype == QTYPE_SELECT:
        query = psycopg2.sql.SQL('SELECT {} FROM events').format(
            psycopg2.sql.SQL(', ').join(
                [psycopg2.sql.Identifier(x) for x in columns]
            )
        )
    elif qtype == QTYPE_COUNT:
        query = psycopg2.sql.SQL('SELECT count(id) FROM events')
    elif qtype == QTYPE_DELETE:
        query = psycopg2.sql.SQL('DELETE FROM events')
    elif isinstance(qtype, psycopg2.sql.Composed):
        query = qtype
    else:
        raise ValueError("Received invalid value '{}' for SQL query type.".format(qtype))

    # Process and append query filtering parameters.
    if parameters:
        if parameters.get('dt_from', None):
            chunks.append(psycopg2.sql.SQL('{} >= %s').format(psycopg2.sql.Identifier('detecttime')))
            params.append(parameters['dt_from'])
        if parameters.get('dt_to', None):
            chunks.append(psycopg2.sql.SQL('{} <= %s').format(psycopg2.sql.Identifier('detecttime')))
            params.append(parameters['dt_to'])
        if parameters.get('st_from', None):
            chunks.append(psycopg2.sql.SQL('{} >= %s').format(psycopg2.sql.Identifier('cesnet_storagetime')))
            params.append(parameters['st_from'])
        if parameters.get('st_to', None):
            chunks.append(psycopg2.sql.SQL('{} <= %s').format(psycopg2.sql.Identifier('cesnet_storagetime')))
            params.append(parameters['st_to'])

        if parameters.get('host_addrs', None):
            _bq_searchby_addr(chunks, params, ['source_ip', 'target_ip'], parameters['host_addrs'])
        else:
            if parameters.get('source_addrs', None):
                _bq_searchby_addr(chunks, params, ['source_ip'], parameters['source_addrs'])
            if parameters.get('target_addrs', None):
                _bq_searchby_addr(chunks, params, ['target_ip'], parameters['target_addrs'])
        if parameters.get('host_ports', None):
            chunks.append(psycopg2.sql.SQL('({} && %s OR {} && %s)').format(psycopg2.sql.Identifier('source_port'), psycopg2.sql.Identifier('target_port')))
            params.extend([parameters['host_ports'], [int(x) for x in parameters['host_ports']]])
        else:
            if parameters.get('source_ports', None):
                chunks.append(psycopg2.sql.SQL('{} && %s').format(psycopg2.sql.Identifier('source_port')))
                params.append([int(x) for x in parameters['source_ports']])
            if parameters.get('target_ports', None):
                chunks.append(psycopg2.sql.SQL('{} && %s').format(psycopg2.sql.Identifier('target_port')))
                params.append([int(x) for x in parameters['target_ports']])
        if parameters.get('host_types', None):
            chunks.append(psycopg2.sql.SQL('({} && %s OR {} && %s)').format(psycopg2.sql.Identifier('source_type'), psycopg2.sql.Identifier('target_type')))
            params.extend([parameters['host_types'], parameters['host_types']])
        else:
            if parameters.get('source_types', None):
                chunks.append(psycopg2.sql.SQL('{} && %s').format(psycopg2.sql.Identifier('source_type')))
                params.append(parameters['source_types'])
            if parameters.get('target_types', None):
                chunks.append(psycopg2.sql.SQL('{} && %s').format(psycopg2.sql.Identifier('target_type')))
                params.append(parameters['target_types'])

        for item in (
                ('protocols',       'protocol',                _bq_param_multi_to_array),
                ('categories',      'category',                _bq_param_multi_to_array),
                ('classes',         'cesnet_eventclass',       _bq_param_multi_to_scalar),
                ('severities',      'cesnet_eventseverity',    _bq_param_multi_to_scalar),
                ('detectors',       'node_name',               _bq_param_multi_to_array),
                ('detector_types',  'node_type',               _bq_param_multi_to_array),
                ('groups',          'cesnet_resolvedabuses',   _bq_param_multi_to_array),
                ('inspection_errs', 'cesnet_inspectionerrors', _bq_param_multi_to_array),
            ):
            if parameters.get(item[0], None):
                item[2](
                    chunks,
                    params,
                    item[1],
                    parameters.get(item[0]),
                    parameters.get('not_{}'.format(item[0]), False)
                )

        if parameters.get('description', None):
            chunks.append(psycopg2.sql.SQL('{} = %s').format(psycopg2.sql.Identifier('description')))
            params.append(parameters['description'])

    if chunks:
        query += psycopg2.sql.SQL(' WHERE ')
        query += psycopg2.sql.SQL(' AND ').join(chunks)

    # Process and append query sorting and limiting parameters.
    if qtype == QTYPE_SELECT and parameters:
        if parameters.get('sortby', None):
            field, direction = parameters['sortby'].split('.')
            if field == 'detecttime':
                field = 'detecttime'
            elif field == 'storagetime':
                field = 'cesnet_storagetime'
            else:
                if parameters.get('st_from', None) or parameters.get('st_to', None):
                    field = 'cesnet_storagetime'
                else:
                    field = 'detecttime'
            if direction in ('asc',):
                query += psycopg2.sql.SQL(' ORDER BY {} ASC').format(psycopg2.sql.Identifier(field))
            else:
                query += psycopg2.sql.SQL(' ORDER BY {} DESC').format(psycopg2.sql.Identifier(field))

        if parameters.get('limit', None):
            query += psycopg2.sql.SQL(' LIMIT %s')
            params.append(int(parameters['limit']))

            if 'page' in parameters and parameters['page'] and int(parameters['page']) > 1:
                query += psycopg2.sql.SQL(' OFFSET %s')
                params.append((int(parameters['page']) - 1) * int(parameters['limit']))

    return query, params


class IPListAdapter():
    """
    Adapt a :py:class:`mentat.idea.sqldb.IPList` to an SQL quotable object.

    Resources: http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax
    """

    def __init__(self, seq):
        self._seq = seq

    def prepare(self, conn):
        """
        Implementation of ``psycopg2`` adapter interface.
        """

    def getquoted(self):
        """
        Implementation of ``psycopg2`` adapter interface.
        """
        qobjs = [str(o) for o in self._seq]
        return "'{" + ', '.join(qobjs) + "}'"

    __str__ = getquoted

class IPBaseAdapter():
    """
    Adapt a :py:class:`ipranges.IPBase` to an SQL quotable object.

    Resources: http://initd.org/psycopg/docs/advanced.html#adapting-new-python-types-to-sql-syntax
    """

    def __init__(self, rng):
        self._rng = rng

    def prepare(self, conn):
        """
        Implementation of ``psycopg2`` adapter interface.
        """

    def getquoted(self):
        """
        Implementation of ``psycopg2`` adapter interface.
        """
        return "'{}'".format(str(self._rng))

    __str__ = getquoted


def record_to_idea(val):
    """
    Convert given SQL record object, as fetched from PostgreSQL database, directly
    into :py:class:`mentat.idea.internal.Idea` object.
    """
    return mentat.idea.internal.Idea.from_json(
        val.event.tobytes().decode('utf-8')
    )

def record_to_idea_ghost(val):
    """
    Convert given SQL record object, as fetched from PostgreSQL database, directly
    into :py:class:`mentat.idea.internal.IdeaGhost` object.
    """
    return mentat.idea.internal.IdeaGhost.from_record(val)


class EventStorageCursor:
    """
    Encapsulation of :py:class:`psycopg2.cursor` class.
    """
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastquery = None

    def __del__(self):
        self.close()

    def __getattr__(self, name):
        return getattr(self.cursor, name)

    def close(self):
        """
        Close current database connection.
        """
        try:
            self.cursor.close()
        except:  # pylint: disable=locally-disabled,bare-except
            pass
        self.cursor = None

    #---------------------------------------------------------------------------

    def insert_event(self, idea_event):
        """
        Insert given IDEA message into database.

        :param mentat.idea.internal idea_event: Instance of IDEA message.
        """
        idea_pgsql = mentat.idea.sqldb.Idea(idea_event)
        record = idea_pgsql.get_record()
        self.cursor.execute(
            "INSERT INTO events (id, detecttime, category, description, source_ip, target_ip, source_ip_aggr_ip4, source_ip_aggr_ip6, target_ip_aggr_ip4, target_ip_aggr_ip6, source_port, target_port, source_type, target_type, protocol, node_name, node_type, cesnet_resolvedabuses, cesnet_storagetime, cesnet_eventclass, cesnet_eventseverity, cesnet_inspectionerrors, event) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            record
        )

    def fetch_event(self, eventid):
        """
        Fetch IDEA message with given primary identifier from database.

        :param str eventid: Primary identifier of the message to fetch.
        :return: Instance of IDEA message.
        :rtype: mentat.idea.internal
        """
        self.cursor.execute(
            "SELECT id, event FROM events WHERE id = %s",
            (eventid,)
        )
        record = self.cursor.fetchone()
        if record:
            return record_to_idea(record)
        return None

    def delete_event(self, eventid):
        """
        Delete IDEA message with given primary identifier from database.

        :param str eventid: Primary identifier of the message to fetch.
        """
        self.cursor.execute(
            "DELETE FROM events WHERE id = %s",
            (eventid,)
        )

    def count_events(self, parameters = None):
        """
        Count the number of IDEA messages in database.

        :param dict parameters: Count query parameters.
        :return: Number of IDEA messages in database.
        :rtype: int
        """
        if not parameters:
            query = "SELECT COUNT(id) FROM events"
            self.lastquery = query
            self.cursor.execute(query)
        else:
            query, params  = build_query(parameters, qtype = 'count')
            self.lastquery = self.cursor.mogrify(query, params)
            self.cursor.execute(query, params)
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def search_events(self, parameters = None, event_factory = record_to_idea, columns = EVENT_COLUMNS):
        """
        Search IDEA messages in database according to given parameters. The
        parameters will be passed down to the :py:func:`mentat.services.eventstorage.build_query`
        function to generate proper SQL query.

        :param dict parameters: Search query parameters, see :py:func:`mentat.services.eventstorage.build_query` for details.
        :param callable event_factory: Conversion callback method to use to convert each record.
        """
        query, params  = build_query(parameters, columns = columns)
        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        event_count = self.cursor.rowcount
        events_raw  = self.cursor.fetchall()
        return event_count, [event_factory(event) for event in events_raw]

    def search_column_with(self, column, function = 'min'):
        """
        Search given column with given aggregation function. This method is intended
        to produce single min or max values for given column name.
        """
        if function not in ('min', 'max'):
            raise ValueError('Invalid function for column search')
        sql_raw = 'SELECT {}({{}}) FROM events'.format(function)

        query = psycopg2.sql.SQL(sql_raw).\
            format(psycopg2.sql.Identifier(column))
        self.lastquery = self.cursor.mogrify(query)

        self.cursor.execute(query)
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def watchdog_events(self, interval):
        """
        Perform watchdog operation on event database: Check if any new events were
        added into the database within given time interval.

        :param int interval: Desired time interval in seconds.
        :return: ``True`` in case any events were stored within given interval, ``False`` otherwise.
        :rtype: bool
        """
        params = ('{:d}s'.format(interval),)
        query = psycopg2.sql.SQL("SELECT max({}) > NOW() AT TIME ZONE 'GMT' - INTERVAL %s AS watchdog FROM events").\
            format(psycopg2.sql.Identifier('cesnet_storagetime'))
        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        record = self.cursor.fetchone()
        if record:
            return record[0] is True
        return False

    def delete_events(self, parameters = None):
        """
        Delete IDEA messages in database according to given parameters.

        :param dict parameters: Delete query parameters.
        :return: Number of deleted events.
        :rtype: int
        """
        query, params  = build_query(parameters, qtype = 'delete')
        self.lastquery = self.cursor.mogrify(query, params)

        self.cursor.execute(query, params)
        return self.cursor.rowcount

    #---------------------------------------------------------------------------

    def table_cleanup(self, table, column, ttl):
        """
        Clean expired table records according to given TTL.

        :param str table: Name of the table to cleanup.
        :param str column: Name of the column holding the time information.
        :param datetime.datetime ttl: Maximal valid TTL.
        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute(
            psycopg2.sql.SQL("DELETE FROM {} WHERE {} < %s").format(
                psycopg2.sql.Identifier(table),
                psycopg2.sql.Identifier(column)
            ),
            (ttl,)
        )
        return self.cursor.rowcount

    #---------------------------------------------------------------------------

    def threshold_set(self, key, thresholdtime, relapsetime, ttl):
        """
        Insert new threshold record into the thresholding cache.

        :param str key: Record key to the thresholding cache.
        :param datetime.datetime thresholdtime: Threshold window start time.
        :param datetime.datetime relapsetime: Relapse window start time.
        :param datetime.datetime ttl: Record TTL.
        """
        self.cursor.execute(
            "INSERT INTO thresholds (id, thresholdtime, relapsetime, ttltime) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET thresholdtime = EXCLUDED.thresholdtime, relapsetime = EXCLUDED.relapsetime, ttltime = EXCLUDED.ttltime",
            (key, thresholdtime, relapsetime, ttl)
        )

    def threshold_check(self, key, ttl):
        """
        Check thresholding cache for record with given key.

        :param str key: Record key to the thresholding cache.
        :param datetime.datetime ttl: Upper TTL boundary for valid record.
        :return: Full cache record as tuple.
        :rtype: tuple
        """
        self.cursor.execute(
            "SELECT * FROM thresholds WHERE id = %s AND ttltime >= %s",
            (key, ttl)
        )
        result_raw = self.cursor.fetchall()
        return result_raw

    def threshold_save(self, eventid, keyid, group_name, severity, createtime):
        """
        Save given event to the list of thresholded events.

        :param str eventid: Unique event identifier.
        :param str keyid: Record key to the thresholding cache.
        :param str group_name: Name of the abuse group.
        :param str severity: Event severity.
        :param datetime.datetime createtime: Record creation time.
        """
        self.cursor.execute(
            "INSERT INTO events_thresholded (eventid, keyid, groupname, eventseverity, createtime) VALUES (%s, %s, %s, %s, %s)",
            (eventid, keyid, group_name, severity, createtime)
        )

    def thresholds_count(self):
        """
        Count threshold records in thresholding cache.

        :return: Number of records in thresholding cache.
        :rtype: int
        """
        self.cursor.execute(
            "SELECT count(*) FROM thresholds",
        )
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def thresholds_clean(self, ttl):
        """
        Clean no longer valid threshold records from thresholding cache.

        :param datetime.datetime ttl: Maximal valid TTL.
        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute(
            "DELETE FROM thresholds WHERE ttltime < %s",
            (ttl,)
        )
        return self.cursor.rowcount

    def search_relapsed_events(self, group_name, severity, ttl):
        """
        Search for list of relapsed events for given group, severity and TTL.
        Event is considered to be relapsed, when following conditions are met:

        * there is record in ``thresholds`` table with ``thresholds.ttltime <= $ttl``
          (this means that thresholding window expired)
        * there is record in ``events_thresholded`` table with ``events_thresholded.createtime >= thresholds.relapsetime``
          (this meant that the event was thresholded in relapse period)

        :param str group_name: Name of the abuse group.
        :param str severity: Event severity.
        :param datetime.datetime ttl: Record TTL time.
        :return: List of relapsed events as :py:class:`mentat.idea.internal.Idea` objects.
        :rtype: list
        """
        self.cursor.execute(
            "SELECT * FROM events WHERE id IN (SELECT DISTINCT eventid FROM events_thresholded WHERE keyid IN (SELECT keyid FROM events_thresholded INNER JOIN thresholds ON (events_thresholded.keyid = thresholds.id) WHERE events_thresholded.groupname = %s AND events_thresholded.eventseverity = %s AND events_thresholded.createtime >= thresholds.relapsetime AND thresholds.ttltime <= %s))",
            (group_name, severity, ttl)
        )
        events_raw  = self.cursor.fetchall()
        return [record_to_idea(event) for event in events_raw]

    def thresholded_events_count(self):
        """
        Count number of records in list of thresholded events.

        :return: Number of records in list of thresholded events.
        :rtype: int
        """
        self.cursor.execute(
            "SELECT count(*) FROM events_thresholded",
        )
        record = self.cursor.fetchone()
        if record:
            return record[0]
        return None

    def thresholded_events_clean(self):
        """
        Clean no longer valid records from list of thresholded events. Record is
        no longer valid in following cases:

        * there is no appropriate record in ``thresholds`` table
          (there is no longer active thresholding window)
        * the ``events_thresholded.createtime < thresholds.relapsetime``
          (there is an active thresholding window, but event does not belong to relapse interval)

        :return: Number of cleaned up records.
        :rtype: int
        """
        self.cursor.execute(
            "DELETE FROM events_thresholded WHERE NOT EXISTS (SELECT * FROM thresholds WHERE thresholds.id = events_thresholded.keyid)"
        )
        count_orphaned = self.cursor.rowcount

        self.cursor.execute(
            "DELETE FROM events_thresholded WHERE keyid IN (SELECT keyid FROM events_thresholded INNER JOIN thresholds ON (events_thresholded.keyid = thresholds.id) WHERE events_thresholded.createtime < thresholds.thresholdtime)"
        )
        count_timeouted = self.cursor.rowcount

        return count_orphaned + count_timeouted


class EventStorageService:
    """
    Proxy object for working with persistent SQL based event storages. Maintains
    and provides access to database connection.
    """

    def __init__(self, **conncfg):
        """
        Open and cache connection to event storage. The connection arguments for
        database engine are passed directly to :py:func:`psycopg2.connect`method.

        :param conncfg: Connection arguments.
        """
        conncfg['cursor_factory'] = psycopg2.extras.NamedTupleCursor
        if not hasattr(self, "dsn"):
            self.dsn = conncfg
        self.connection = psycopg2.connect(**self.dsn)
        self.cursor     = None
        self.cursor_new()

    def __del__(self):
        self.close()

    def close(self):
        """
        Close current database connection.
        """
        try:
            self.cursor.close()
            self.connection.close()
        except:  # pylint: disable=locally-disabled,bare-except
            pass
        self.cursor     = None
        self.connection = None

    def commit(self):
        """
        Commit currently pending changes into persistent storage.
        """
        self.connection.commit()

    def rollback(self):
        """
        Rollback currently pending changes into persistent storage.
        """
        self.connection.rollback()

    def mogrify(self, query, parameters):
        """
        Format given SQL query, replace placeholders with given parameters and
        return resulting SQL query as string.
        """
        return self.cursor.mogrify(query, parameters)

    def cursor_new(self):
        """
        Create new database cursor.
        """
        if self.cursor:
            self.cursor.close()
        self.cursor = EventStorageCursor(self.connection.cursor())
        return self.cursor

    def handle_db_exceptions(func):
        """
        Handle exceptions raised during database interfacing operations.
        """
        def exc_handle_wrapper(self, *args, **kwargs):
            exc_store = None
            for _ in range(2):
                try:
                    return func(self, *args, **kwargs)

                except psycopg2.DataError as err:
                    self.rollback()
                    raise DataError(str(err)) from err

                except (psycopg2.OperationalError, psycopg2.InterfaceError) as err:
                    self.__init__()
                    exc_store = err
                    continue

                except psycopg2.IntegrityError as err:
                    self.rollback()
                    raise StorageIntegrityError(str(err)) from err

                except psycopg2.DatabaseError as err:
                    self.rollback()
                    raise EventStorageException(str(err)) from err

            raise EventStorageException("DB connection error during data access") from exc_store

        return exc_handle_wrapper

    @handle_db_exceptions
    def database_create(self):
        """
        Create database SQL schema.
        """
        # Base list of CREATE TABLE SQLs.
        create_table_sqls = [
            "CREATE TABLE IF NOT EXISTS events(id text PRIMARY KEY, detecttime timestamp NOT NULL, category text[] NOT NULL, description text, source_ip iprange[], target_ip iprange[], source_ip_aggr_ip4 ip4r, source_ip_aggr_ip6 ip6r, target_ip_aggr_ip4 ip4r, target_ip_aggr_ip6 ip6r, source_port integer[], target_port integer[], source_type text[], target_type text[], protocol text[], node_name text[] NOT NULL, node_type text[], cesnet_storagetime timestamp NOT NULL, cesnet_resolvedabuses text[], cesnet_eventclass text, cesnet_eventseverity text, cesnet_inspectionerrors text[], event bytea)",
            "CREATE TABLE IF NOT EXISTS thresholds(id text PRIMARY KEY, thresholdtime timestamp NOT NULL, relapsetime timestamp NOT NULL, ttltime timestamp NOT NULL)",
            "CREATE TABLE IF NOT EXISTS events_thresholded(eventid text NOT NULL, keyid text NOT NULL, groupname text NOT NULL, eventseverity text NOT NULL, createtime timestamp NOT NULL, PRIMARY KEY(eventid, keyid))"
        ]

        # Generate list of CREATE TABLE SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            create_table_sqls.append(
                psycopg2.sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} (data text UNIQUE NOT NULL, last_seen TIMESTAMP WITHOUT TIME ZONE NOT NULL)"
                ).format(
                    psycopg2.sql.Identifier(
                        "enum_{}".format(column_name)
                    )
                )
            )

        for query in create_table_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def index_create(self):
        """
        Create default set of table indices.
        """
        # Base list of CREATE INDEX SQLs.
        create_index_sqls = [
            "CREATE INDEX IF NOT EXISTS events_detecttime_idx ON events USING BTREE (detecttime)",
            "CREATE INDEX IF NOT EXISTS events_cesnet_storagetime_idx ON events USING BTREE (cesnet_storagetime)",
            "CREATE INDEX IF NOT EXISTS events_cesnet_eventseverity_idx ON events USING BTREE (cesnet_eventseverity) WHERE cesnet_eventseverity IS NOT NULL",
            "CREATE INDEX IF NOT EXISTS events_combined_idx ON events USING GIN (category, node_name, protocol, source_port, target_port, source_type, target_type, node_type, cesnet_resolvedabuses, cesnet_inspectionerrors)",
            "CREATE INDEX IF NOT EXISTS thresholds_thresholdtime_idx ON thresholds USING BTREE (thresholdtime)",
            "CREATE INDEX IF NOT EXISTS thresholds_relapsetime_idx ON thresholds USING BTREE (relapsetime)",
            "CREATE INDEX IF NOT EXISTS thresholds_ttltime_idx ON thresholds USING BTREE (ttltime)",
            "CREATE INDEX IF NOT EXISTS events_thresholded_combined_idx ON events_thresholded USING BTREE (groupname, eventseverity)",
            "CREATE INDEX IF NOT EXISTS events_thresholded_createtime_idx ON events_thresholded USING BTREE (createtime)"
        ]

        # Generate list of CREATE INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            create_index_sqls.append(
                psycopg2.sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} USING BTREE (last_seen)"
                ).format(
                    psycopg2.sql.Identifier(
                        "enum_{}_lastseen_idx".format(column_name)
                    ),
                    psycopg2.sql.Identifier(
                        "enum_{}".format(column_name)
                    )
                )
            )

        for query in create_index_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def database_drop(self):
        """
        Drop database SQL schema.
        """
        # Base list of DROP TABLE SQLs.
        drop_table_sqls = [
            "DROP TABLE IF EXISTS events",
            "DROP TABLE IF EXISTS thresholds",
            "DROP TABLE IF EXISTS events_thresholded"
        ]

        # Generate list of CREATE INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            drop_table_sqls.append(
                psycopg2.sql.SQL(
                    "DROP TABLE IF EXISTS {}"
                ).format(
                    psycopg2.sql.Identifier(
                        "enum_{}".format(column_name)
                    )
                )
            )

        for query in drop_table_sqls:
            self.cursor.execute(query)
            self.commit()

    @handle_db_exceptions
    def index_drop(self):
        """
        Drop default set of table indices.
        """
        # Base list of DROP INDEX SQLs.
        drop_index_sqls = [
            "DROP INDEX IF EXISTS events_detecttime_idx",
            "DROP INDEX IF EXISTS events_cesnet_storagetime_idx",
            "DROP INDEX IF EXISTS events_cesnet_resolvedabuses_idx",
            "DROP INDEX IF EXISTS events_cesnet_eventseverity_idx",
            "DROP INDEX IF EXISTS events_combined_idx",
            "DROP INDEX IF EXISTS thresholds_thresholdtime_idx",
            "DROP INDEX IF EXISTS thresholds_relapsetime_idx",
            "DROP INDEX IF EXISTS thresholds_ttltime_idx",
            "DROP INDEX IF EXISTS events_thresholded_combined_idx",
            "DROP INDEX IF EXISTS events_thresholded_createtime_idx"
        ]

        # Generate list of DROP INDEX SQLs for column value enumeration tables.
        for column_name in ENUM_TABLES:
            drop_index_sqls.append(
                psycopg2.sql.SQL(
                    "DROP INDEX IF EXISTS {} "
                ).format(
                    psycopg2.sql.Identifier(
                        "enum_{}_lastseen_idx".format(column_name)
                    )
                )
            )
        for query in drop_index_sqls:
            self.cursor.execute(query)
            self.commit()

    #---------------------------------------------------------------------------

    @handle_db_exceptions
    def insert_event(self, idea_event):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.insert_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.insert_event(idea_event)
        self.commit()

    @handle_db_exceptions
    def fetch_event(self, eventid):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.fetch_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.fetch_event(eventid)
        self.commit()
        return result

    @handle_db_exceptions
    def delete_event(self, eventid):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.delete_event`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.delete_event(eventid)
        self.commit()

    @handle_db_exceptions
    def count_events(self, parameters = None):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.count_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.count_events(parameters)
        self.commit()
        return result

    @handle_db_exceptions
    def search_events(self, parameters = None, event_factory = record_to_idea, columns = EVENT_COLUMNS):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count, result = self.cursor.search_events(parameters, event_factory, columns)
        self.commit()
        return count, result

    @handle_db_exceptions
    def search_column_with(self, column, function = 'min'):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_column_with`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.search_column_with(column, function)
        self.commit()
        return result

    @handle_db_exceptions
    def watchdog_events(self, interval):
        """
        Perform watchdog operation on event database: Check if any new events were
        added into the database within given time interval.

        :param int interval: Desired time interval in seconds.
        :return: ``True`` in case any events were stored within given interval, ``False`` otherwise.
        :rtype: bool
        """
        result = self.cursor.watchdog_events(interval)
        self.commit()
        return result

    @handle_db_exceptions
    def delete_events(self, parameters = None):
        """
        Delete IDEA messages in database according to given optional parameters.
        These parameters will

        :param dict parameters: Optional delete query parameters.
        :return: Number of deleted events.
        :rtype: int
        """
        count = self.cursor.delete_events(parameters)
        self.commit()
        return count

    @handle_db_exceptions
    def distinct_values(self, column):
        """
        Return distinct values of given table column.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.

        :param str column: Name of the column to query for distinct values.
        :return: List of distinct values.
        :rtype: list
        """
        enum_table = "enum_{}".format(column)
        # Build and execute query for updating enumeration table.
        enum_query = psycopg2.sql.SQL("INSERT INTO {} (SELECT * FROM (").format(psycopg2.sql.Identifier(enum_table))
        if column not in ('cesnet_eventclass', 'cesnet_eventseverity'):
            enum_query += psycopg2.sql.SQL("SELECT unnest({})").format(psycopg2.sql.Identifier(column))
        else:
            enum_query += psycopg2.sql.SQL("SELECT {}").format(psycopg2.sql.Identifier(column))
        enum_query += psycopg2.sql.SQL(' AS data, max(cesnet_storagetime) AS last_seen FROM events WHERE cesnet_storagetime >= COALESCE((SELECT max(last_seen) FROM {}), (SELECT min(cesnet_storagetime) FROM events)) GROUP BY data) AS enum WHERE data IS NOT NULL) ON CONFLICT (data) DO UPDATE SET last_seen = excluded.last_seen').format(psycopg2.sql.Identifier(enum_table))
        self.cursor.execute(enum_query)
        self.commit()

        # Return all entries from recetly updated enumeration table.
        self.cursor.execute(
            psycopg2.sql.SQL("SELECT data FROM {} ORDER BY data").format(psycopg2.sql.Identifier(enum_table))
        )
        result_raw = self.cursor.fetchall()
        self.commit()
        return [item[0] for item in result_raw if item[0] is not None]

    @handle_db_exceptions
    def table_cleanup(self, table, column, ttl):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.table_cleanup`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.table_cleanup(table, column, ttl)
        self.commit()
        return count

    @handle_db_exceptions
    def threshold_set(self, key, thresholdtime, relapsetime, ttl):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_set`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.threshold_set(key, thresholdtime, relapsetime, ttl)
        self.commit()

    @handle_db_exceptions
    def threshold_check(self, key, threshold):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_check`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.threshold_check(key, threshold)
        self.commit()
        return result

    @handle_db_exceptions
    def threshold_save(self, eventid, keyid, group_name, severity, createtime):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.threshold_save`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        self.cursor.threshold_save(eventid, keyid, group_name, severity, createtime)
        self.commit()

    @handle_db_exceptions
    def thresholds_count(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholds_count`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.thresholds_count()
        self.commit()
        return result

    @handle_db_exceptions
    def thresholds_clean(self, threshold):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholds_clean`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.thresholds_clean(threshold)
        self.commit()
        return count

    @handle_db_exceptions
    def search_relapsed_events(self, group_name, severity, ttl):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.search_relapsed_events`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        events = self.cursor.search_relapsed_events(group_name, severity, ttl)
        self.commit()
        return events

    @handle_db_exceptions
    def thresholded_events_count(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholded_events_count`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        result = self.cursor.thresholded_events_count()
        self.commit()
        return result

    @handle_db_exceptions
    def thresholded_events_clean(self):
        """
        This method is a convenience wrapper for underlying
        :py:func:`mentat.services.eventstorage.EventStorageCursor.thresholded_events_clean`
        method.

        It will automatically commit transaction for successfull database operation
        and rollback the invalid one.
        """
        count = self.cursor.thresholded_events_clean()
        self.commit()
        return count

    #---------------------------------------------------------------------------

    def table_status(self, table_name, time_column):
        """
        Determine status of given table within current database.
        """
        result = {}

        self.cursor.execute(
            psycopg2.sql.SQL(
                "SELECT *, pg_size_pretty(total_bytes) AS total\
                    , pg_size_pretty(index_bytes) AS INDEX\
                    , pg_size_pretty(toast_bytes) AS toast\
                    , pg_size_pretty(table_bytes) AS TABLE\
                FROM (\
                    SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (\
                        SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME\
                            , c.reltuples AS row_estimate\
                            , pg_total_relation_size(c.oid) AS total_bytes\
                            , pg_indexes_size(c.oid) AS index_bytes\
                            , pg_total_relation_size(reltoastrelid) AS toast_bytes\
                        FROM pg_class c\
                        LEFT JOIN pg_namespace n ON n.oid = c.relnamespace\
                        WHERE relkind = 'r' AND relname = %s\
                    ) a\
                ) a;"
            ),
            [table_name]
        )
        data_raw = self.cursor.fetchone()
        self.commit()
        result.update(
            table_name      = data_raw.table_name,
            row_estimate    = data_raw.row_estimate,
            total_bytes     = data_raw.total_bytes,
            index_bytes     = data_raw.index_bytes,
            toast_bytes     = data_raw.toast_bytes,
            table_bytes     = data_raw.table_bytes,
            total_bytes_str = data_raw.total,
            index_bytes_str = data_raw.index,
            toast_bytes_str = data_raw.toast,
            table_bytes_str = data_raw.table
        )

        self.cursor.execute(
            psycopg2.sql.SQL("SELECT MIN({}) as minvalue FROM {}").format(
                psycopg2.sql.Identifier(time_column),
                psycopg2.sql.Identifier(table_name)
            )
        )
        record = self.cursor.fetchone()
        self.commit()
        if record:
            result['dt_oldest'] = record.minvalue

        self.cursor.execute(
            psycopg2.sql.SQL("SELECT MAX({}) as maxvalue FROM {}").format(
                psycopg2.sql.Identifier(time_column),
                psycopg2.sql.Identifier(table_name)
            )
        )
        record = self.cursor.fetchone()
        self.commit()
        if record:
            result['dt_newest'] = record.maxvalue

        return result

    def database_status(self, brief = False):
        """
        Determine status of all tables within current database and general
        PostgreSQL configuration.
        """
        result = {'tables': {}}

        #---

        if not brief:
            self.cursor.execute(
                "SELECT * FROM pg_settings"
            )
            records = self.cursor.fetchall()
            self.commit()
            result['pg_settings'] = {rec.name: rec for rec in records}

        #---

        table_wanted_list = [
            ('events', 'cesnet_storagetime'),
            ('events_thresholded', 'createtime'),
            ('thresholds', 'ttltime')
        ]
        for column_name in ENUM_TABLES:
            table_wanted_list.append(
                (
                    "enum_{}".format(column_name),
                    "last_seen"
                )
            )

        for table_name in table_wanted_list:
            result['tables'][table_name[0]] = self.table_status(*table_name)

        return result


class EventStorageServiceManager:
    """
    Class representing a custom _EventStorageServiceManager_ capable of understanding
    and parsing Mentat system core configurations.
    """

    def __init__(self, core_config, updates = None):
        """
        Initialize a _EventStorageServiceManager_ proxy object with full core configuration
        tree structure.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = {}
        self._storage = None
        self._configure_dbconfig(core_config, updates)

    def _configure_dbconfig(self, core_config, updates):
        """
        Internal sub-initialization helper: Configure database structure parameters
        and optionally merge them with additional updates.

        :param dict core_config: Mentat core configuration structure.
        :param dict updates: Optional configuration updates (same structure as ``core_config``).
        """
        self._dbconfig = copy.deepcopy(core_config[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_EVENTSTORAGE])

        if updates and CKEY_CORE_DATABASE in updates and CKEY_CORE_DATABASE_EVENTSTORAGE in updates[CKEY_CORE_DATABASE]:
            self._dbconfig.update(
                updates[CKEY_CORE_DATABASE][CKEY_CORE_DATABASE_EVENTSTORAGE]
            )

    #---------------------------------------------------------------------------


    def close(self):
        """
        Close internal storage connection.
        """
        if self._storage:
            self._storage.close()
            self._storage = None

    def service(self):
        """
        Return handle to storage connection service according to internal configurations.

        :return: Reference to storage service.
        :rtype: mentat.services.eventstorage.EventStorageService
        """
        if not self._storage:
            self._storage = EventStorageService(**self._dbconfig)
        return self._storage


#-------------------------------------------------------------------------------


def init(core_config, updates = None):
    """
    (Re-)Initialize :py:class:`mentat.services.eventstorage.EventStorageServiceManager`
    instance at module level and store the refence within module.

    :param dict core_config: Mentat core configuration structure.
    :param dict updates: Optional configuration updates (same structure as ``core_config``).
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = EventStorageServiceManager(core_config, updates)


def set_manager(man):
    """
    Set manager from outside of the module. This should be used only when you know
    exactly what you are doing.
    """
    global _MANAGER  # pylint: disable=locally-disabled,global-statement
    _MANAGER = man


def manager():
    """
    Obtain reference to :py:class:`mentat.services.eventstorage.EventStorageServiceManager`
    instance stored at module level.

    :return: Storage service manager reference.
    :rtype: mentat.services.eventstorage.EventStorageServiceManager
    """
    return _MANAGER


def service():
    """
    Obtain reference to :py:class:`mentat.services.eventstorage.EventStorageService`
    instance from module level manager.

    :return: Storage service reference.
    :rtype: mentat.services.eventstorage.EventStorageService
    """
    return manager().service()


def close():
    """
    Close database connection on :py:class:`mentat.services.eventstorage.EventStorageService`
    instance from module level manager.
    """
    return manager().close()


#
# Register custom psycopg2 adapter for adapting lists of IP addressess into SQL
# query.
#
psycopg2.extensions.register_adapter(mentat.idea.sqldb.IPList, IPListAdapter)
psycopg2.extensions.register_adapter(ipranges.IPBase, IPBaseAdapter)
