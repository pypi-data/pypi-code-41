#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import logging
from datetime import datetime

from braincube.bc_connector.braincube_requests import Requester
from braincube.bc_connector.entities.braincube import Braincube
from braincube.bc_connector.entities.memorybase import Memorybase

logger = logging.getLogger(__name__)


class RawRetriever:  # Class giving access to functions communicating with the braincube API
    def __init__(self, sso_token, braincubes):
        self.__sso_token = sso_token
        self.__braincubes = braincubes

    def get_braincube_list(self):
        # Return a dataframe containing the braincubes accessible
        return self.__braincubes

    def get_memorybase_list(self, braincube_name):
        # Return a dataframe containing the memorybases available for the braincube selected
        try:
            requester = Requester(braincube_name, self.__sso_token)
            return requester.get_memorybase()
        except json.decoder.JSONDecodeError:
            logger.error("Invalid parameters, please check spelling or access rights")

    def get_memorybase_order_variable(self, braincube_name, mb_id):
        # Return the id of the variable which is used to order the memorybase
        try:
            requester = Requester(braincube_name, self.__sso_token)
            return requester.get_references(mb_id)
        except json.decoder.JSONDecodeError:
            logger.error("Invalid parameters, please check spelling or access rights")

    def get_variable_list(self, braincube_name, mb_id):
        # Return a dataframe containing the variables available for the memorybase selected
        try:
            requester = Requester(braincube_name, self.__sso_token)
            return requester.get_data_defs(mb_id)
        except json.decoder.JSONDecodeError:
            logger.error("Invalid parameters, please check spelling or access rights")

    def retrieve_all_variables_from_memory_base(self, braincube_name, mb_id, start_date, end_date=datetime.now()):
        # Return a dataframe containing the datas of all the variables of the selected memorybase
        # Indexed with the order variable, a column represents a variable
        variable_list = self.get_variable_list(braincube_name, mb_id)
        selected_variables = []
        for var in variable_list:
            selected_variables.append(var['id'])
        return self.retrieve_data(braincube_name, mb_id, selected_variables, start_date, end_date)

    def retrieve_data(self, braincube_name, mb_id, variable_list, start_date, end_date=datetime.now()):
        start_time = datetime.now().timestamp()
        # Return a dataframe containing the datas of the seelcted variables for the selected memorybase
        # Indexed with the order variable, a column represents a variable
        logger.info(
            "Working on : [Braincube: {braincube_name}, MemoryBase: {mb_id}]".format(braincube_name=braincube_name,
                                                                                     mb_id=str(mb_id)))
        try:
            requester = Requester(braincube_name, self.__sso_token)
            ref = requester.get_references(mb_id)
            selected_variables = []
            for var in variable_list:
                selected_variables.append(ref['name'] + '/d' + str(var))
            datas = requester.request_data(ref, selected_variables,
                                           start_date.strftime("%Y%m%d_%H%M%S"),
                                           end_date.strftime("%Y%m%d_%H%M%S"))

            end_time = datetime.now().timestamp()
            logger.info("Raw data retrieved [cols:{cols}, lines:{lines}] in {duration} s".format(
                cols=str(len(selected_variables)),
                lines=str(datas['resultLength']),
                duration="{0:.2f}".format(end_time - start_time)))
            return datas['datadefs']
        except json.decoder.JSONDecodeError:
            logger.error("Invalid parameters, please check spelling or access rights")

    def get_braincube(self, braincube_name):
        return Braincube(braincube_name, self)

    def get_memorybase(self, braincube_name, mb_id):
        return Memorybase(braincube_name, mb_id, self)
