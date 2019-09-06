#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


def get_data_with_id(data):
    # Transforms the data into a dictionary with the variable's id and the corresponding data for that variable
    var = {}
    for i in data:
        var[i['id'].split('/d')[1]] = i['data']
    return var


def data_to_dataframe(datas, datadefs, ref):
    logger.debug('Start converting to Pandas dataFrame')
    start_time = datetime.now().timestamp()
    # Return a dataframe based on the given data
    data = get_data_with_id(datas)
    index = []
    result = {}
    for datadef in datadefs:
        intent = str(datadef['id'])
        if intent in data.keys():
            extent = data[intent]
            if intent == ref['referenceDate'].split('/d')[1]:
                for j in range(len(extent)):  # Changes the format of the date to be readable
                    extent[j] = datetime.strptime(extent[j], "%Y%m%d_%H%M%S") \
                        .strftime("%Y/%m/%d_%H:%M:%S")
                index = extent
            else:
                result[datadef['local']] = extent
    dataframe = pd.DataFrame(result, index=index)

    end_time = datetime.now().timestamp()
    duration = "{0:.2f}".format(end_time - start_time)
    logger.info("Conversion to Pandas DataFrame in " + str(duration) + " s")
    return dataframe
