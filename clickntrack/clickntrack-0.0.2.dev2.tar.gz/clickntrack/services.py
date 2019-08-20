#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging

from clickntrack.persistence import EntryDAO


class Service:

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def count_all(self):
        raise NotImplementedError()

    def list(self, skip=0, limit=10, sort_key='_id', sort_dir='1'):
        raise NotImplementedError()

    def get_one_by_id(self, uid):
        raise NotImplementedError()

    def create(self, **kwargs):
        raise NotImplementedError()

    def bulk_create(self, data):
        raise NotImplementedError()

    def update(self, **kwargs):
        raise NotImplementedError()

    def delete_one_by_id(self, uid):
        raise NotImplementedError()


class EntryService(Service):

    def __init__(self, dao: EntryDAO):
        super().__init__()
        self.dao: EntryDAO = dao

    def count_all(self):
        return self.dao.count()

    def list(self, skip=0, limit=10, sort_key='_id', sort_dir='1'):
        # TODO: Change sort setting
        return self.dao.find_all(skip, limit, [(sort_key, sort_dir)])

    def get_one_by_id(self, uid):
        return self.dao.find_one_by_key(uid)

    def create(self, host, short_name, target):
        """ Create a new entry"""
        inserted_id = self.dao.insert_one(host, short_name, target)
        return inserted_id

    def bulk_create(self, data):
        return self.dao.insert(data)

    def update(self, **kwargs):
        raise NotImplementedError()

    def delete_one_by_id(self, iud):
        return self.dao.delete(iud)

    def get_target_url(self, host, short_name, channel, referer, user_agent, remote_addr):
        entry = self.dao.find_one_by_host_and_short_name(host, short_name)
        self.dao.add_hit(host, short_name, channel, referer, user_agent, remote_addr)
        target = entry['target']
        return target

    def get_one_by_host_and_short_name(self, host, short_name):
        entry = self.dao.find_one_by_host_and_short_name(host, short_name)
        return entry
