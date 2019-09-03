#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of Mentat system (https://mentat.cesnet.cz/).
#
# Copyright (C) since 2011 CESNET, z.s.p.o (http://www.ces.net/)
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Daemon component capable of storing IDEA messages into persistent storage.
Currently only `PostgreSQL <https://www.postgresql.org/>`__ database is supported.

It is dependent on services of following modules:

* :py:mod:`mentat.services.eventstorage`

  Interface for working with persistent storage.

The implementation is based on :py:class:`pyzenkit.zendaemon.ZenDaemonComponent`.

"""


__author__ = "Jan Mach <jan.mach@cesnet.cz>"
__credits__ = "Pavel Kácha <pavel.kacha@cesnet.cz>, Andrea Kropáčová <andrea.kropacova@cesnet.cz>"


import datetime
import traceback


#
# Custom libraries
#
import pyzenkit.zendaemon
import pynspect.jpath
import mentat.services.eventstorage


class StorageDaemonComponent(pyzenkit.zendaemon.ZenDaemonComponent):
    """
    Daemon component capable of storing IDEA messages into database.
    """
    EVENT_MSG_PROCESS    = 'message_process'
    EVENT_LOG_STATISTICS = 'log_statistics'

    STATS_CNT_STORED = 'cnt_stored'
    STATS_CNT_ERRORS = 'cnt_errors'

    def __init__(self, **kwargs):
        """
        Perform component initializations.
        """
        super().__init__(**kwargs)

        # Unique component identifier
        self.cid = kwargs.get('cid', 'storage')

        self.eventservice = None

        # Permit changing of default event mapping
        self.event_map = kwargs.get('event_map', {
            self.EVENT_MSG_PROCESS:    self.EVENT_MSG_PROCESS,
            self.EVENT_LOG_STATISTICS: self.EVENT_LOG_STATISTICS
        })

    def setup(self, daemon):
        """
        Perform component setup.
        """
        esm = mentat.services.eventstorage.EventStorageServiceManager(daemon.config)
        self.eventservice = esm.service()
        daemon.logger.debug(
            "[STATUS] Component '{}': Set up event storage service.".format(
                self.cid
            )
        )

    def get_events(self):
        """
        Get the list of event names and their appropriate callback handlers.
        """
        return [
            {
                'event': self.event_map[self.EVENT_MSG_PROCESS],
                'callback': self.cbk_event_message_process,
                'prepend': False
            },
            {
                'event': self.event_map[self.EVENT_LOG_STATISTICS],
                'callback': self.cbk_event_log_statistics,
                'prepend': False
            }
        ]

    #---------------------------------------------------------------------------

    def cbk_event_message_process(self, daemon, args):
        """
        Store the message into the persistent storage.
        """
        daemon.logger.debug(
            "Component '{}': Storing message '{}':'{}'.".format(
                self.cid,
                args['id'],
                args['idea_id']
            )
        )
        try:
            # Set current time as _CESNET.StorageTime.
            pynspect.jpath.jpath_set(args['idea'], '_CESNET.StorageTime', datetime.datetime.utcnow())

            # Attempt to store IDEA message into database.
            self.eventservice.insert_event(args['idea'])
            daemon.logger.info(
                "Component '{}': Stored message '{}':'{}' into database.".format(
                    self.cid,
                    args['id'],
                    args['idea_id']
                )
            )

            self.inc_statistic(self.STATS_CNT_STORED)
            return (daemon.FLAG_CONTINUE, args)

        except:  # pylint: disable=locally-disabled,bare-except
            daemon.logger.error(
                "Component '{}': Unable to store IDEA message '{}' into database: '{}'".format(
                    self.cid,
                    args['id'],
                    traceback.format_exc()
                )
            )
            daemon.queue.schedule('message_banish', args)

            self.inc_statistic(self.STATS_CNT_ERRORS)
            return (daemon.FLAG_STOP, args)

    def cbk_event_log_statistics(self, daemon, args):
        """
        Periodical processing statistics logging.
        """
        stats = self.get_statistics()
        stats_str = ''

        for k in [self.STATS_CNT_STORED, self.STATS_CNT_ERRORS]:
            if k in stats:
                stats_str = self.pattern_stats.format(stats_str, k, stats[k]['cnt'], stats[k]['inc'], stats[k]['spd'])
            else:
                stats_str = self.pattern_stats.format(stats_str, k, 0, 0, 0)

        daemon.logger.info(
            "Component '{}': *** Processing statistics ***{}".format(
                self.cid,
                stats_str
            )
        )
        return (daemon.FLAG_CONTINUE, args)
