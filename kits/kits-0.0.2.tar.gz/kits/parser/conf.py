# -*- coding: utf-8 -*-

import logging
import traceback
import ast

class ConfParser(object):

    _parser = None
    _conf   = dict()

    def __init__(self):
        import configparser
        self._parser = configparser.ConfigParser()


    def load(self, conf_file=None):
        '''
        load config data from conf file
        :param conf_file:
        :return:
        '''
        if not conf_file:
            raise ValueError("Cannot find file.")

        self._parser.read(conf_file, encoding='UTF-8')
        self.assemble()

    @property
    def config(self):
        '''
        get conf
        :return:
        '''
        return self._conf

    def parse(self, section, options):
        '''
        parse config
        :param section:
        :param options:
        :return:
        '''
        if section not in self._conf:
            self._conf[section] = dict()

        for option in options:
            config = self._parser.get(section, option)
            try:
                config = ast.literal_eval(config)
            except Exception as e:
                logging.error(traceback.format_exc())

            self._conf[section][option] = config

    def assemble(self):
        '''
        assemble config
        :return:
        '''
        if self._parser.sections():
            for section in self._parser.sections():
                options = self._parser.options(section)
                self.parse(section, options)
