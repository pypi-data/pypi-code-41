#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import sys

import pymongo
import pymongo.errors

from monkey.dao.core import PersistenceError, ObjectNotFoundError
from monkey.dao.pymongo.core import PyMongoDAO

__author__ = 'Xavier ROY'


class EntryDAO(PyMongoDAO):
    _COLLECTION_NAME = 'entries'

    _AUDITABLE = True

    def __init__(self, database):
        super().__init__(database, EntryDAO._COLLECTION_NAME, True)
        self.auditable = EntryDAO._AUDITABLE

    def find_one_by_host_and_short_name(self, host, short_name):
        """ Get a shortened URL entry
        :param host: The hostname of the shortened URL
        :param short_name: The 'short name' used in shortened URL (a.k.a path component of the URL)
        :return: The entry matching hostname and 'short name'
        """
        try:
            entry = self.collection.find_one({'host': host, 'shortName': short_name})
            if entry is not None:
                return entry
            else:
                raise ObjectNotFoundError(self.collection.name, {'host': host, 'short_name': short_name})
        except pymongo.errors.PyMongoError as e:
            raise PersistenceError('Unexpected error', e)

    def get_entries_by_short_name(self, short_name, skip=0, limit=-1):
        """ Lists entries matching the specified short name
        :param short_name: The 'short name' used in shortened URL (a.k.a path component of the URL)
        :param skip: The number of skipped entries.
        :param limit: The maximum number of returned entries
        :return: Entries matching the 'short name'
        """
        try:
            cursor = self.collection.find({'shortName': short_name}).sort('host', direction=1).skip(skip).limit(limit)
            entries = []
            for entry in cursor:
                entries.append(entry)
            return entries
        except pymongo.errors.PyMongoError as e:
            raise PersistenceError('Unexpected error', e)

    def insert_one(self, host, short_name, target):
        """ Inserts a new entry
        :param host: The hostname of the shortened URL
        :param short_name: The 'short name' used in shortened URL (a.k.a path component of the URL)
        :param target: The target URL where the shortened URL redirects to.
        :return: id of the inserted entry
        """
        # Build a new entry
        data_set = {'host': host,
                    'shortName': short_name,
                    'target': target}
        self.insert(data_set)

    def add_hit(self, host, short_name, channel, referer, user_agent, remote_addr):
        """ Add a hit on a shortened URL
        :param host: The hostname of the shortened URL
        :param short_name: The 'short name' used in shortened URL (a.k.a path component of the URL)
        :param channel: The channel specified in the shortened URL hit
        :param referer: The HTTP referer of the request
        :param user_agent: The user agent of the request
        :param remote_addr: The remote address of the request
        :return: Number of modified entries. It ever should be 1 or 0 (non existing shortened URL)
        """
        hit = {'timestamp': datetime.datetime.utcnow(), 'channel': channel, 'referer': referer, 'userAgent': user_agent,
               'remoteAddr': remote_addr}
        try:
            result = self.collection.update_one({'host': host, 'shortName': short_name},
                                                {'$push': {'hits': hit}, '$inc': {'hitCount': 1}})
            return result.modified_count
        except pymongo.errors.PyMongoError as e:
            self.logger.error('Failed to add hit on {}/{}/{}'.format(host, short_name, channel))
            self.logger.error('Unexpected error: {}'.format(sys.exc_info()[0]))
            raise PersistenceError('Unexpected error', e)
