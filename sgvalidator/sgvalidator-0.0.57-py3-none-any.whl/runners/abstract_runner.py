from abc import ABCMeta
from ..data_preprocessor import DataPreprocessor


class AbstractRunner:
    __metaclass__ = ABCMeta

    @staticmethod
    def filterData(data, config):
        countryFilter = config.getCountryFilter()
        if data.empty:
            return data
        elif countryFilter is not None:
            copied = data.loc[data[DataPreprocessor.DETECTED_CC] == countryFilter].copy()
            if copied.empty:
                return copied
            return copied
        else:
            return data
