#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API
import datetime
import logging

log = logging.getLogger(__name__)


class Parameters(API):
    """
    CHIME/FRB Parameters API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_node_info(self, node_name: str = None):
        """
        Get CHIME/FRB Compute Node Information

        Parameters
        ----------
        node_name : str
            CHIME/FRB Compute Node Name, e.g. cf1n1

        Returns
        -------
        dict
        """
        try:
            assert isinstance(node_name, str), "node_name is required, e.g. cf1n1"
            return self._get("/v1/parameters/get-node-info/{}".format(node_name))
        except AssertionError as e:
            raise NameError(e)

    def get_beam_info(self, beam_number: int = None):
        """
        Get CHIME/FRB Beam Information

        Parameters
        ----------
        beam_number : int
            CHIME/FRB Beam Number, e.g. 2238

        Returns
        -------
        dict
        """
        try:
            assert isinstance(beam_number, int), "int required"
            assert 0 < beam_number % 1000 < 256, "antenna id range [0,255]"
            assert 0 < beam_number / 1000 < 4, "cylinder id range [0,3]"
            return self._get("/v1/parameters/get-beam-info/{}".format(beam_number))
        except AssertionError as e:
            raise TypeError("invalid beam_number {}".format(e))

    def get_frame0_nano(event_date: datetime = None):
        """
        Get the frame0_nano for any given UTC Timestamp

        Parameters
        ----------
            event_date : datetime object
            Datetime object containing the time of the event

        Returns
        -------
            frame0_nano : float
            frame0_nano time for the event datetime

        Raises
        ------
            RuntimeError
        """
        raise NotImplemented
