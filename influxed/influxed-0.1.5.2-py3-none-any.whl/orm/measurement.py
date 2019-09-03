#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: measurement.py
 File Created: Monday, 18th February 2019 12:17:35 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.orm.columns import TagKey, FieldKey
from influxed.orm.capabilities.showable import Showable
from influxed.orm.capabilities.queryable import Queryable
from influxed.orm.capabilities.insertable import Insertable
from influxed.orm.capabilities.asyncable import HandlePosibleAsync
from influxed.ifql.util import KEY_WORDS


class Measurement(Showable, Queryable, Insertable):
    """
        Class definition of a measurement

        Contains definitions of columns (field keys and field tags)
    """
    
    @property
    def connection_string(self):
        return self.database.connection_string

    @property
    def username(self):
        return self.database.username
    
    @property
    def mediator(self):
        return self.database.mediator

    @property
    def database(self):
        return self.__database__

    def set_database(self, val):
        self.__database__ = val
        return self
    
    @property
    def columns(self):
        if(not hasattr(self, '__columns__')):
            self.__columns__ = {}
        return self.__columns__
    
    @columns.setter
    def columns(self, value):
        self.__columns__ = value
    
    def add_column(self, col):
        if(not isinstance(col, (TagKey, FieldKey))):
            raise Exception('Only TagKeys and FieldKeys are allowed')
        
        self.columns[col.name] = col
        if(isinstance(col, TagKey)):
            self.tags[col.name] = col
        if(isinstance(col, FieldKey)):
            self.fields[col.name] = col

    @property
    def tags(self):
        if(not hasattr(self, '__tag_keys__')):
            self.__tag_keys__ = {}
        return self.__tag_keys__
    
    @tags.setter
    def tags(self, value):
        self.__tag_keys__ = value
    
    @property
    def fields(self):
        if(not hasattr(self, '__field_keys__')):
            self.__field_keys__ = {}
        return self.__field_keys__
    
    @fields.setter
    def fields(self, value):
        self.__field_keys__ = value

    @property
    def name(self):
        return self.__measurement__

    @name.setter
    def name(self, value):
        self.__measurement__ = value
  
    def __show_prefix__(self, show_statement):
        """
            Overwrite from showable
        """
        return self.database.__show_prefix__(show_statement).from_(self.name)

    def __select_prefix__(self, select_statement):
        """
            Overwrite from showable
        """
        return select_statement.from_(self.name)

    def __insert_prefix__(self, insert_statement):
        return self.database.__insert_prefix__(insert_statement).measurement(self.name)

    def __getattr__(self, name):
        if(name in ('__columns__', '__tag_keys__', '__field_keys__')):
            raise AttributeError
        if(name in self.columns):
            return self.columns[name]
        raise AttributeError

    def __getitem__(self, item):
        return self.__columns__[item]

    def reflect(self):
        if(self.database.name == '_internal'):
            return []
        possible_future = HandlePosibleAsync(self.__look_up_keys__())
        possible_future.chain_function(self.__create_orm_keys__)
        return possible_future.return_()

    def __create_orm_keys__(self, fields_keys):
        tags, fields = fields_keys
        # Reflect tags keys
        if(tags is not None and not isinstance(tags, list) and not tags.empty):
            for tagKey in tags.tagKey:
                self.add_column(TagKey(tagKey).set_measurement(self))
        
        # Reflect field keys
        if(fields is not None and not isinstance(fields, list) and not fields.empty):
            for field in fields.fieldKey:
                self.add_column(FieldKey(field).set_measurement(self))

    def __look_up_keys__(self):
        tags = self.show(KEY_WORDS.TAG_KEYS).all()
        fields = self.show(KEY_WORDS.FIELD_KEYS).all()
        return (tags, fields)

    def ls(self, prefix=''):
        for k in self.tags.keys():
            print(prefix+' Tag: '+k)
        for k in self.fields.keys():
            print(prefix+' Field: '+k)



