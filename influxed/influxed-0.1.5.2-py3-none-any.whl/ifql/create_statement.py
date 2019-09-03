#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
 File: create_statement.py
 File Created: Thursday, 21st February 2019 9:55:23 pm
 Author: ESR - Romeren (emilromer@hotmail.com)
 -----
 Copyright 2019 OpenSourced, OpenSourced
 -----
 Last Modified:
 Date	By	Comments
 -----
"""

from influxed.ifql.statement import CommonStatementFormatter
from influxed.ifql.util import KEY_WORDS
from influxed.ifql.util import PRIVILEGES
from influxed.ifql.util import INTERVAL
from influxed.ifql.exceptions import MissingArgument

def create_statement(key_word=None, hook=None):
    if(key_word == None):
            return WrapperCreateStatement(hook)
    if(key_word == KEY_WORDS.DATABASES):
        return CreateDatabaseStatementBuilder(key_word, hook=hook)
    if(key_word == KEY_WORDS.RETENTION_POLICIES):
        return CreateRetentionPolicyStatementBuilder(key_word, hook=hook)
    if(key_word == KEY_WORDS.USERS):
        return CreateUserStatementBuilder(key_word, hook=hook)


class WrapperCreateStatement(object):
    def __init__(self, hook):
        self.hook = hook

    @property
    def database(self):
        return CreateDatabaseStatementBuilder(KEY_WORDS.DATABASES, hook=self.hook)

    @property
    def replication_policy(self):
        return CreateRetentionPolicyStatementBuilder(KEY_WORDS.RETENTION_POLICIES, hook=self.hook)

    @property
    def user(self):
        return CreateUserStatementBuilder(KEY_WORDS.USERS, hook=self.hook)

class CommonCreate(CommonStatementFormatter):

    def format_create(self):
        return NotImplementedError

    def _format(self):
        print('NOT IMPLEMENTED')
        return self.format_create()

class CommonRetention(CommonCreate):
    __is_duration_optional__ = True
    __is_replication_optional__ = True

    def __init__(self, hook=None):
        self.__duration__ = None
        self.__replication__ = None
        self.__shard_duration__ = None
        super(CommonRetention, self).__init__(hook=hook)

    def duration(self, duration):
        if(isinstance(duration, str)):
            self.__duration__ = INTERVAL.parse_interval_str(duration)
        elif(isinstance(duration, INTERVAL)):
            self.__duration__ = duration
        return self
    
    def replication(self, replication):
        if(replication < 1):
            raise ValueError('Replication must be a positive non zero integer')
        self.__replication__ = replication
        return self 
    
    def shard_duration(self, shard_duration):
        self.__shard_duration__ = shard_duration
        return self

    def format_duration(self):
        if(not self.__is_duration_optional__ and not self.__duration__):
            raise MissingArgument('Missing argument duration!')
        if(not self.__duration__):
            return ''
        return 'DURATION ' + self.__duration__.format()

    def format_replication(self):
        if(not self.__is_replication_optional__ and not self.__replication__):
            raise MissingArgument('Missing argument replication!')
        if(not self.__replication__):
            return ''

        return 'REPLICATION ' + str(self.__replication__)
    
    def format_shard_duration(self):
        if(not self.__shard_duration__):
            return ''
        return 'SHARD DURATION ' + self.__shard_duration__

class CreateDatabaseStatementBuilder(CommonRetention):
    """
        CREATE DATABASE <database_name> [WITH [DURATION <duration>] [REPLICATION <n>] [SHARD DURATION <duration>] [NAME <retention-policy-name>]]
    """
    def __init__(self, create_key_word, hook=None):
        self._name_ = None
        self.create_key_word = create_key_word
        self.__retention_policy_name__ = None
        CommonRetention.__init__(self, hook=hook)

    def name(self, name):
        self._name_ = name
        return self

    def retention_name(self, retention_policy_name):
        self.__retention_policy_name__ = retention_policy_name
        return self 

    def format_retention_policy_name(self):
        if(not self.__retention_policy_name__):
            return ''
        return 'NAME ' + self.__retention_policy_name__

    def format_create(self):
        """
            CREATE DATABASE <database_name> [WITH [DURATION <duration>] [REPLICATION <n>] [SHARD DURATION <duration>] [NAME <retention-policy-name>]]
        """
        if(self._name_ is None):
            raise MissingArgument('Missing argument name')
        statement =  'CREATE DATABASE ' + self._name_
        if(self.__duration__ or self.__replication__ or self.__shard_duration__ or self.__retention_policy_name__):
            statement += ' WITH '
        
        statement += ' '.join([ x for x in [
            self.format_duration(),
            self.format_replication(),
            self.format_shard_duration(),
            self.format_retention_policy_name()
        ] if x ])

        return statement

class CreateRetentionPolicyStatementBuilder(CommonRetention):
    """
        CREATE RETENTION POLICY <retention_policy_name> ON <database_name> DURATION <duration> REPLICATION <n> [SHARD DURATION <duration>] [DEFAULT]
    """
    __is_duration_optional__ = False
    __is_replication_optional__ = False

    def __init__(self, create_key_word, hook=None):
        self.create_key_word = create_key_word
        self.__database__ = None
        self.__default__ = False
        self.__name__ = None
        super(CreateRetentionPolicyStatementBuilder, self).__init__(hook=hook)
    
    def name(self, name):
        self.__name__ = name
        return self
    
    def on(self, database):
        self.__database__ = database
        return self
    
    def default(self, is_default):
        """
            Optional
        """
        self.__default__ = is_default
        return self

    def format_default(self):
        if(not self.__default__):
            return ''
        return 'TRUE'

    def format_create(self):
        if(not self.__name__ or not self.__database__):
            raise MissingArgument('Missing argument name=' + str(self.__name__)+', database=' + str(self.__database__))
        statement = 'CREATE RETENTION POLICY '+self.__name__+' ON '+self.__database__+' '+self.format_duration()+' '+self.format_replication()
        statement += ' '.join([ x for x in [
            self.format_shard_duration(),
            self.format_default()
        ] if x ])
        return statement

class CreateUserStatementBuilder(CommonCreate):
    """
    CREATE USER <username> WITH PASSWORD '<password>' WITH ALL PRIVILEGES
    """

    def __init__(self, create_key_word, hook=None):
        CommonCreate.__init__(self, hook=hook)
        self.create_key_word = create_key_word
        self.__previleges__ = None
        self.__username__ = None
        self.__password__ = None

    def username(self, username):
        self.__username__ = username
        return self
    
    def password(self, password):
        self.__password__ = password
        return self

    def previleges(self, previleges):
        self.__previleges__ = previleges
        return self

    def format_previleges(self):
        if(not self.__previleges__):
            return ''
        if(isinstance(self.__previleges__, PRIVILEGES)):
            return self.__previleges__.value
        return self.__previleges__

    def format_create(self):
        if(not self.__username__ or not self.__password__):
            raise MissingArgument('Missing argument username='+str(self.__username__)+' or password='+str(self.__password__))
        statement = "CREATE USER "+self.__username__+" WITH PASSWORD '"+self.__password__+"'"
        statement = ' '.join([ x for x in [
            statement, self.format_previleges()
        ] if x])
        return statement