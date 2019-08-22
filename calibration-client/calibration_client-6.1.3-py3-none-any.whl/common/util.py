"""Util Class with helper methods"""
import datetime
from time import gmtime, strftime


class Util(object):
    @staticmethod
    def get_formatted_date(dt_format, epoch_val=None, dt_extra=None):
        # formatted_time_str
        if epoch_val is None:
            formatted_time_str = strftime(dt_format, gmtime())
        else:
            formatted_time_str = strftime(dt_format, gmtime(epoch_val))

        # timezone
        if dt_extra is None:
            fractional_and_timezone = ''
        else:
            fractional_and_timezone = dt_extra

        return '{0}{1}'.format(formatted_time_str, fractional_and_timezone)

    @staticmethod
    def val_to_api_bool(value_in):
        val_type = type(value_in)

        if val_type in (int, bool):
            val_str = str(value_in)
        else:
            val_str = str(value_in)
            return 'Error: Value {0} is of type {1}'.format(val_str, val_type)

        if val_str == '1' or val_str == 'True':
            return 'true'
        else:
            return 'false'

    @staticmethod
    def get_opt_hash_val(h, element_name, def_val=''):
        if element_name in h:
            return h[element_name]
        else:
            return def_val

    @staticmethod
    def datetime_converter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
