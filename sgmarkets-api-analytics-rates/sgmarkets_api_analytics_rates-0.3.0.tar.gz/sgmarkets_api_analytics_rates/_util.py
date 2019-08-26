
import pandas as pd

from collections import OrderedDict


class Util:

    @staticmethod
    def get_unique_list(my_list):
        """
        """
        unique_list = list(OrderedDict((e, None) for e in my_list))
        unique_list = [e for e in unique_list if pd.notnull(e)]
        return unique_list

    @staticmethod
    def build_url(dic_url):
        return '{}{}{}'.format(dic_url['base_url'], dic_url['service'], dic_url['endpoint'])

    @staticmethod
    def date_to_str(ts):
        """
        """
        return ts.strftime('%Y-%m-%d')
