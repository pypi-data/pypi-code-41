#!/usr/bin/env python
# -*- coding: utf-8 -*-

from chime_frb_api.core import API
import datetime
import logging
import typing as t

log = logging.getLogger(__name__)

INT_ARGS = ["beam_number"]
FLOAT_ARGS = [
    "dm",
    "dm_error",
    "width",
    "width_error",
    "snr",
    "dm_index",
    "dm_index_error",
    "flux",
    "flux_error",
    "fluence",
    "fluence_error",
    "spectral_running",
    "spectral_running_error",
    "frequency_mean",
    "frequency_mean_error",
    "frequency_width",
    "frequency_width_error",
    "scattering_index",
    "scattering_index_error",
    "scattering_timescale",
    "scattering_timescale_error",
    "linear_polarization_fraction",
    "linear_polarization_fraction_error",
    "circular_polarization_fraction",
    "circular_polarization_fraction_error",
    "spectral_index",
    "spectral_index_error",
    "rotation_measure",
    "rotation_measure_error",
    "redshift_host",
    "redshift_host_error",
    "dispersion_smearing",
    "dispersion_smearing_error",
    "spin_period",
    "spin_period_error",
    "ra",
    "ra_error",
    "dec",
    "dec_error",
    "gl",
    "gb",
    "system_temperature",
]
DICT_ARGS = ["galactic_dm", "pipeline"]
LIST_ARGS = ["gain", "expected_spectrum"]
VALID_ARGS = INT_ARGS + FLOAT_ARGS + DICT_ARGS + LIST_ARGS


class Events(API):
    """
    CHIME/FRB Events API

    Attributes
    ----------
    base_url : str
        Base URL at which the is accessible.
    """

    def __init__(self, base_url: str = "http://frb-vsop.chime:8001"):
        API.__init__(self, base_url=base_url)

    def get_event(self, event_number: int = None, full_header: bool = False):
        """
        Get CHIME/FRB Event Information

        Parameters
        ----------
        event_number : int
            CHIME/FRB Event Number

        full_header : bool
            Get the full event from L4, default is False

        Returns
        -------
        dict
        """
        if event_number is None:
            return "event_number is required."
        if full_header:
            return self._get("/v1/events/full-header/{}".format(event_number))
        else:
            return self._get("/v1/events/{}".format(event_number))

    def add_measured_parameters(
        self, event_number: int = None, measured_parameters: t.List[dict] = None
    ):
        """
        Append a new set of measured parameters to CHIME/FRB Event

        Parameters
        ----------
            measured_parameters : [dict]

            list of a dictionary of measured parameters to update, 
            valid values for each item in the list are
            pipeline : {
                    name : str
                        Name of the pipeline used to generate measured parameters
                    status: str
                        Status of the Pipeline
                            SCHEDULED
                            IN PROGRESS
                            COMPLETE
                            ERROR
                            UNKNOWN
                    log: str
                        Small message describing the pipeline run.
                    version:
                        version of the pipeline used to make the measured parameters
                }
                dm : float
                dm_error : float
                width : float
                width_error : float
                snr : float
                dm_index : float
                dm_index_error : float
                flux : float
                flux_error : float
                fluence : float
                fluence_error : float
                spectral_running : float
                spectral_running_error : float
                frequency_mean : float
                frequency_mean_error : float
                frequency_width : float
                frequency_width_error : float
                scattering_index : float
                scattering_index_error : float
                scattering_timescale : float
                scattering_timescale_error : float
                linear_polarization_fraction : float
                linear_polarization_fraction_error : float
                circular_polarization_fraction : float
                circular_polarization_fraction_error : float
                spectral_index : float
                spectral_index_error : float
                rotation_measure : float
                rotation_measure_error : float
                redshift_host : float
                redshift_host_error : float
                dispersion_smearing : float
                dispersion_smearing_error : float
                spin_period : float
                spin_period_error : float
                ra : float
                ra_error : float
                dec : float
                dec_error : float
                gl : float
                gb : float
                system_temperature : float
                beam_number : int
                galactic_dm : dict
                gain : list
                expected_spectrum: list
        Returns
        -------
            db_response : dict
        """
        try:
            assert measured_parameters is not None, "measured parameters are required"
            if not isinstance(measured_parameters, list):
                measured_parameters = [measured_parameters]
            assert event_number is not None, "event_number is required"
            for item in measured_parameters:
                assert "pipeline" in item.keys(), "pipeline dictionary is required"
                assert "name" in item["pipeline"].keys(), "pipeline name is required"
                assert (
                    "status" in item["pipeline"].keys()
                ), "pipeline status is required"
                assert (
                    len(item.keys()) > 1
                ), "no parameters updated"  # pipeline is already 1 key
        except AssertionError as e:
            raise NameError(e)

        payloads = []
        try:
            for item in measured_parameters:
                payload = {}
                # Check if the args are valid
                for key, value in item.items():
                    assert key in VALID_ARGS, "invalid parameter key <{}>".format(key)
                    self._check_arg_type(key, value)
                    payload[key] = value
                payloads.append(payload)
            url = "/v1/events/measured-parameters/{}".format(event_number)
            response = self._put(url=url, payload=payloads)
            return response
        except AssertionError as e:
            raise NameError(e)
        except TypeError as e:
            raise TypeError(e)
        except Exception as e:
            raise e

    def _check_arg_type(self, key, value):
        try:
            if key in INT_ARGS:
                if not isinstance(value, int):
                    raise TypeError(key)
            elif key in FLOAT_ARGS:
                if not isinstance(value, float):
                    raise TypeError(key)
            elif key in DICT_ARGS:
                if not isinstance(value, dict):
                    raise TypeError(key)
            elif key in LIST_ARGS:
                if not isinstance(value, list):
                    raise TypeError(key)
        except TypeError as e:
            raise TypeError("invalid parameter type <{}, {}>".format(key, value))
