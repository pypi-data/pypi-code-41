#!/usr/bin/env python
# -*- coding:utf-8 -*-
from datetime import datetime


class Memorybase:
    def __init__(self, braincube_name, mb_id, retriever):
        self.__retriever = retriever
        self.__braincube = braincube_name
        self.__mb_id = mb_id

    def get_memorybase_order_variable(self):
        """
        :return: the id of the variable which is used to order the memorybase
        """
        return self.__retriever.get_memorybase_order_variable(self.__braincube, self.__mb_id)

    def get_variable_list(self):
        """
        :return: a list of the variables available for the memorybase
        """
        return self.__retriever.get_variable_list(self.__braincube, self.__mb_id)

    def retrieve_all_variables_from_memory_base(self, start_date, end_date=datetime.now()):
        """
        :param start_date: a datetime value from which we want to filter (mandatory)
        :param end_date: a datetime value to which we want to filter (datetime.now() by default)
        :return: the datas of all the variables of the memorybase. (one column per variable)
        """
        return self.__retriever.retrieve_all_variables_from_memory_base(self.__braincube, self.__mb_id, start_date,
                                                                        end_date)

    def retrieve_data(self, variable_list, start_date, end_date=datetime.now()):
        """
        :param variable_list: a list of variable ids as strings
        :param start_date:  a datetime value from which we want to filter (no default)
        :param end_date: end_date: a datetime value to which we want to filter (datetime.now() by default)
        :return: the datas of the selected variables of the memorybase (one column per variable).
        """
        return self.__retriever.retrieve_data(self.__braincube, self.__mb_id, variable_list,
                                              start_date, end_date)
