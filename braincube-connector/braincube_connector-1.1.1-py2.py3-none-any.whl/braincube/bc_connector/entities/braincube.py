#!/usr/bin/env python
# -*- coding:utf-8 -*-


class Braincube:
    def __init__(self, braincube_name, retriever):
        self.__retriever = retriever
        self.__name = braincube_name

    def get_memorybase_list(self):
        """
        :return: the list of memoryBase available
        """
        return self.__retriever.get_memorybase_list(self.__name)

    def get_memorybase(self, mb_id):
        """
        :param mb_id: a string with the memoryBase id
        :return: a memorybase entity
        """
        return self.__retriever.get_memorybase(self.__name, mb_id)
